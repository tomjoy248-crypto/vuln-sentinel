// Auto-generated from static/index.html body content.

// Pages mount this content into #app on first render.

export const APP_TEMPLATE = `</head>

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

`;



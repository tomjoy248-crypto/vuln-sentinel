let lastFixerResult = null;
let lastTicketContext = null;

function loadTicketContextFromStorage() {
  try {
    let raw = localStorage.getItem('vs_fixer_ticket');
    if (!raw) return;
    let ticket = JSON.parse(raw);
    if (!ticket || !ticket.url) return;
    lastTicketContext = ticket;
    let inp = document.getElementById('fixer-input');
    if (inp && !inp.value.trim()) {
      inp.value = ticket.url + '\n\n# 来源工单\n# ' + (ticket.ticket_id || '') + '\n# ' + (ticket.finding_name || '') + '\n# ' + (ticket.finding_type || '');
    }
    let prompt = document.getElementById('fixer-scan-prompt');
    if (prompt) {
      prompt.innerHTML = '<div class="card-title">已接收工单上下文</div>' +
        '<p style="font-size:13px;color:var(--text-secondary);line-height:1.7;margin:0">已从工单自动带入目标地址，你可以直接分析当前配置并生成修复方案。</p>' +
        '<div style="margin-top:10px;font-size:12px;color:var(--text-secondary)">工单 #' + escapeHtml(String(ticket.ticket_id || '')) + ' · ' + escapeHtml(ticket.finding_name || '') + '</div>';
    }
    localStorage.removeItem('vs_fixer_ticket');
  } catch (e) {}
}
export function loadSampleConfig() {
  try {
    let sample = 'server {\n    listen 80;\n    server_name example.com www.example.com;\n    root /var/www/html;\n    index index.html index.php;\n\n    location / {\n        try_files $uri $uri/ =404;\n    }\n\n    location ~ \\.php$ {\n        fastcgi_pass unix:/run/php/php-fpm.sock;\n        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;\n        include fastcgi_params;\n    }\n\n    access_log /var/log/nginx/access.log;\n    error_log /var/log/nginx/error.log;\n}';
    let inp = document.getElementById('fixer-input');
    if (inp) inp.value = sample;
    showToast('已载入参考 Nginx 配置');
  } catch (e) {
    console.error('loadSampleConfig error:', e);
    showToast('载入参考配置失败: ' + (e.message || String(e)), 'error');
  }
}

export function clearFixer() {
  try {
    if (!confirm("确定要清空当前配置内容吗？")) return;
    let inp = document.getElementById('fixer-input');
    let res = document.getElementById('fixer-result');
    if (inp) inp.value = '';
    if (res) res.innerHTML = '';
    showToast('已清空');
  } catch (e) {
    console.error('clearFixer error:', e);
    showToast('清空失败: ' + (e.message || String(e)), 'error');
  }
}

export function analyzeFixer() {
  setButtonLoading("fixer-analyze-btn", true);
  setTimeout(function(){ setButtonLoading("fixer-analyze-btn", false); }, 600);
  let inputEl = document.getElementById('fixer-input');
  if (!inputEl) return;
  let config = inputEl.value.trim();
  if (!config) {
    showToast('请先输入或粘贴 Nginx 配置');
    return;
  }
  try {
    let result = analyzeNginxConfig(config);
    lastFixerResult = result;
    renderFixerResult(result, config);
  } catch (e) {
    console.error('analyzeFixer error:', e);
    let fr = document.getElementById('fixer-result');
    if (fr) fr.innerHTML = '<div class="card"><p style="color:var(--danger)">分析失败: ' + escapeHtml(e.message || String(e)) + '</p></div>';
  }
}

function analyzeNginxConfig(config) {
  let issues = [];
  let lines = config.split('\n');

  // 1. HSTS
  if (!/Strict-Transport-Security/i.test(config)) {
    issues.push({
      name: 'HSTS 未配置',
      severity: 'high',
      reason: '未设置 Strict-Transport-Security 头，浏览器不会强制使用 HTTPS，可能导致降级攻击。',
      fix: 'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;'
    });
  }

  // 2. CSP
  if (!/Content-Security-Policy/i.test(config)) {
    issues.push({
      name: 'CSP 未配置',
      severity: 'high',
      reason: '未设置 Content-Security-Policy 头，网站容易受到 XSS 攻击和数据注入。',
      fix: 'add_header Content-Security-Policy "default-src \'self\'; script-src \'self\'; style-src \'self\' \'unsafe-inline\'; img-src \'self\' data:; font-src \'self\'; connect-src \'self\'; frame-ancestors \'none\'" always;'
    });
  }

  // 3. X-Frame-Options
  if (!/X-Frame-Options/i.test(config)) {
    issues.push({
      name: 'X-Frame-Options 未配置',
      severity: 'medium',
      reason: '未设置 X-Frame-Options 头，网站可能被嵌入到恶意页面的 iframe 中进行点击劫持攻击。',
      fix: 'add_header X-Frame-Options "DENY" always;'
    });
  }

  // 4. X-Content-Type-Options
  if (!/X-Content-Type-Options/i.test(config)) {
    issues.push({
      name: 'X-Content-Type-Options 未配置',
      severity: 'medium',
      reason: '未设置 X-Content-Type-Options 头，浏览器可能进行 MIME 类型嗅探，导致安全问题。',
      fix: 'add_header X-Content-Type-Options "nosniff" always;'
    });
  }

  // 5. Referrer-Policy
  if (!/Referrer-Policy/i.test(config)) {
    issues.push({
      name: 'Referrer-Policy 未配置',
      severity: 'low',
      reason: '未设置 Referrer-Policy 头，可能泄露敏感 URL 信息给第三方网站。',
      fix: 'add_header Referrer-Policy "strict-origin-when-cross-origin" always;'
    });
  }

  // 6. Permissions-Policy
  if (!/Permissions-Policy/i.test(config)) {
    issues.push({
      name: 'Permissions-Policy 未配置',
      severity: 'low',
      reason: '未设置 Permissions-Policy 头，浏览器可能允许不必要的权限访问（摄像头、麦克风等）。',
      fix: 'add_header Permissions-Policy "camera=(), microphone=(), geolocation=(), payment=()" always;'
    });
  }

  // 7. HTTP -> HTTPS redirect
  let hasSSL = /listen\s+443/i.test(config);
  let hasRedirect = /return\s+301\s+https/i.test(config) || /rewrite.*https/i.test(config);
  if (!hasSSL && !hasRedirect && /listen\s+80/i.test(config)) {
    issues.push({
      name: 'HTTP 到 HTTPS 跳转未配置',
      severity: 'high',
      reason: '仅监听 HTTP 80 端口且未配置 HTTPS 跳转，所有通信为明文传输。',
      fix: 'server {\n    listen 80;\n    server_name _;\n    return 301 https://$host$request_uri;\n}'
    });
  }

  // 8. Sensitive files
  if (!/\.env|deny\s+all|location.*\.(env|git|sql|zip|bak)/i.test(config)) {
    issues.push({
      name: '敏感文件拦截未配置',
      severity: 'high',
      reason: '未配置敏感文件访问拦截规则，.env、.git、.sql 等文件可能被直接访问。',
      fix: 'location ~ /(\\.env|\\.git|\\.gitignore|.*\\.sql|.*\\.zip|.*\\.tar\\.gz|.*\\.bak|.*\\.log|wp-config\\.php) {\n    deny all;\n    return 403;\n}'
    });
  }

  // Generate fixed config
  let fixed = config;
  let securityHeaders = [];
  let securityRules = [];

  issues.forEach(function(issue) {
    if (issue.name === '敏感文件拦截未配置') {
      securityRules.push(issue.fix);
    } else if (issue.name !== 'HTTP 到 HTTPS 跳转未配置') {
      securityHeaders.push(issue.fix);
    }
  });

  if (securityHeaders.length > 0 || securityRules.length > 0) {
    let lastBrace = fixed.lastIndexOf('}');
    if (lastBrace > 0) {
      let before = fixed.substring(0, lastBrace);
      let after = fixed.substring(lastBrace);
      if (securityHeaders.length > 0) {
        securityHeaders.forEach(function(h) {
          before += '    ' + h + '\n';
        });
      }
      if (securityRules.length > 0) {
        securityRules.forEach(function(r) {
          let rlines = r.split('\n');
          rlines.forEach(function(rl) {
            if (rl.trim()) before += '    ' + rl.trim() + '\n';
          });
        });
      }
      fixed = before + after;
    }
  }

  // Generate diff
  let diff = generateDiff(config, fixed);

  return {
    issues: issues,
    fixed: fixed,
    diff: diff
  };
}

function generateDiff(original, fixed) {
  let origLines = original.split('\n');
  let fixedLines = fixed.split('\n');
  let diffLines = [];
  let added = false;

  for (let i = 0; i < fixedLines.length; i++) {
    if (i < origLines.length) {
      if (origLines[i] !== fixedLines[i]) {
        if (!added) {
          diffLines.push({ type: 'context', text: '...' });
          added = true;
        }
        diffLines.push({ type: 'add', text: '+ ' + fixedLines[i] });
      } else {
        if (added && i > 0) {
          diffLines.push({ type: 'context', text: '...' });
          added = false;
        }
        diffLines.push({ type: 'context', text: '  ' + fixedLines[i] });
      }
    } else {
      diffLines.push({ type: 'add', text: '+ ' + fixedLines[i] });
    }
  }

  return diffLines;
}

function renderFixerResult(result, original) {
  try {
    result = result || { issues: [], fixed: '', diff: [] };
    result.issues = result.issues || [];
    result.diff = result.diff || [];
    let html = '';

    // Issues count
    let highCount = 0, medCount = 0, lowCount = 0;
    result.issues.forEach(function(iss) {
      if (iss.severity === 'high') highCount++;
      else if (iss.severity === 'medium') medCount++;
      else lowCount++;
    });

    html += '<div class="card fade-in-up">';
    html += '<div style="display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap;margin-bottom:10px">';
    html += '<div class="card-title" style="margin:0">检测结果</div>';
    if (lastTicketContext) {
      html += '<div style="font-size:12px;color:var(--text-secondary)">来源工单 #' + escapeHtml(String(lastTicketContext.ticket_id || '')) + ' · ' + escapeHtml(lastTicketContext.finding_name || '') + '</div>';
    }
    html += '</div>';
    if (lastTicketContext) {
      html += '<div style="display:flex;gap:8px;flex-wrap:wrap;margin:0 0 12px 0">';
      html += '<button class="fixer-btn secondary" style="padding:6px 12px" onclick="navigateTo(\'tickets\')">返回工单</button>';
      html += '<button class="fixer-btn secondary" style="padding:6px 12px" onclick="navigateTo(\'home\')">回到报告</button>';
      html += '<button class="fixer-btn secondary" style="padding:6px 12px" onclick="localStorage.removeItem(\'vs_fixer_ticket\'); showToast(\'已清除工单来源\')">清除来源</button>';
      html += '</div>';
    }
    html += '<div class="risk-stats" style="margin-bottom:0">';
    html += '<div class="risk-stat high"><div class="num">' + highCount + '</div><div class="label">高严重</div></div>';
    html += '<div class="risk-stat medium"><div class="num">' + medCount + '</div><div class="label">中严重</div></div>';
    html += '<div class="risk-stat low"><div class="num">' + lowCount + '</div><div class="label">低严重</div></div>';
    html += '</div></div>';

    html += '<div class="card fade-in-up" style="animation-delay:0.1s">';
    html += '<div class="card-title">修复点清单</div>';
    result.issues.forEach(function(iss) {
      html += '<div class="issue-item">';
      html += '<span class="issue-severity ' + iss.severity + '">' + (iss.severity === 'high' ? '高' : iss.severity === 'medium' ? '中' : '低') + '</span>';
      html += '<div>';
      html += '<strong>' + escapeHtml(iss.name) + '</strong>';
      html += '<p class="issue-reason">' + escapeHtml(iss.reason) + '</p>';
      html += '</div></div>';
    });
    html += '</div>';

    // Compare
    html += '<div class="card fade-in-up" style="animation-delay:0.2s">';
    html += '<div class="card-title">修复前后对比</div>';
    html += '<div class="compare-grid">';
    html += '<div class="compare-col"><h4><span class="dot red"></span>修复前</h4>';
    html += '<textarea class="compare-textarea" readonly>' + escapeHtml(original) + '</textarea></div>';
    html += '<div class="compare-col"><h4><span class="dot green"></span>修复后 <button class="copy-btn-sm" onclick="copyFixedConfig(this)" data-state="idle" aria-label="复制修复后配置">复制</button></h4>';
    html += '<textarea class="compare-textarea fixed-textarea" readonly>' + escapeHtml(result.fixed) + '</textarea></div>';
    html += '</div></div>';

    // Diff
    html += '<div class="card fade-in-up" style="animation-delay:0.3s">';
    html += '<div class="card-title">Diff 展示</div>';
    html += '<div class="diff-container">';
    result.diff.forEach(function(d) {
      html += '<div class="diff-line ' + d.type + '">' + escapeHtml(d.text) + '</div>';
    });
    html += '</div></div>';

    html += '<div class="card fade-in-up" style="animation-delay:0.4s">';
    html += '<div class="card-title">操作</div>';
    html += '<div class="fixer-btns">';
    html += '<button class="fixer-btn success" onclick="copyFixerResult()">复制修复后配置</button>';
    html += '<button class="fixer-btn primary" onclick="downloadNginxConf()">下载 nginx.conf</button>';
    html += '<button class="fixer-btn success" onclick="downloadRepairReport()">下载修复报告包</button>';
    html += '</div></div>';

    let fr = document.getElementById('fixer-result');
    if (fr) fr.innerHTML = html;
  } catch (e) {
    console.error('renderFixerResult error:', e);
    let fr2 = document.getElementById('fixer-result');
    if (fr2) fr2.innerHTML = '<div class="card"><p style="color:var(--danger)">渲染失败: ' + escapeHtml(e.message || String(e)) + '</p></div>';
  }
}

export function copyFixerResult() {
  let textarea = document.querySelector('#fixer-result .compare-col:last-child textarea');
  if (textarea) {
    copyToClipboard(textarea.value);
    showToast('已复制修复后配置到剪贴板');
  }
}

export function copyFixedConfig(btn) {
  let textarea = btn && btn.closest('.compare-col')
    ? btn.closest('.compare-col').querySelector('textarea')
    : document.querySelector('#fixer-result .compare-col:last-child textarea');
  if (!textarea) return;
  copyToClipboard(textarea.value);
  if (btn) {
    let orig = btn.innerHTML;
    btn.innerHTML = '已复制';
    btn.disabled = true;
    setTimeout(function() { btn.innerHTML = orig; btn.disabled = false; }, 1500);
  }
  showToast('已复制修复后配置到剪贴板');
}

export function downloadNginxConf() {
  let textarea = document.querySelector('#fixer-result .compare-col:last-child textarea');
  if (!textarea) return;
  let content = textarea.value;
  let blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
  let url = URL.createObjectURL(blob);
  let a = document.createElement('a');
  a.href = url;
  a.download = 'nginx.conf';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  showToast('nginx.conf 已下载');
}

export async function downloadRepairReport() {
  if (!lastFixerResult) { showToast('请先分析配置'); return; }
  let r = lastFixerResult;
  let issues = Array.isArray(r.issues) ? r.issues : [];
  let zip = new JSZip();
  let report = '=== Vuln Sentinel 修复报告包 ===\n';
  report += '生成时间：' + new Date().toLocaleString('zh-CN') + '\n';
  report += '报告类型：修复建议与复测清单\n';
  if (lastTicketContext) {
    report += '来源工单：#' + (lastTicketContext.ticket_id || '') + ' · ' + (lastTicketContext.finding_name || '') + '\n';
    report += '来源扫描：#' + (lastTicketContext.scan_id || '') + ' · ' + (lastTicketContext.finding_type || '') + '\n';
  }
  report += '\n--- 原始风险 ---\n';
  issues.forEach(function(issue, i) {
    report += (i + 1) + '. [' + String(issue.severity || '').toUpperCase() + '] ' + (issue.name || '') + '\n';
    report += '   原因：' + (issue.reason || '') + '\n';
  });
  report += '\n--- 修复项 ---\n';
  issues.forEach(function(issue, i) {
    report += (i + 1) + '. ' + (issue.name || '') + '：已修复\n';
  });
  report += '\n--- 修复后配置 ---\n';
  report += (r.fixed || '') + '\n';
  report += '\n--- 复测建议 ---\n';
  report += '1. 使用 curl -I 检查响应头是否包含安全头\n';
  report += '2. 访问 /.env 等敏感路径应返回 403\n';
  report += '3. 使用 SSL Labs 检测 HTTPS 配置\n';
  report += '4. 检查 Content-Security-Policy 是否生效\n';
  zip.file('repair-report.txt', report);
  zip.file('report-summary.json', JSON.stringify({
    generated_at: new Date().toISOString(),
    issues_count: issues.length,
    ticket: lastTicketContext || null,
    has_fixed_code: !!(r.fixed && String(r.fixed).trim())
  }, null, 2));
  let blob = await zip.generateAsync({ type: 'blob' });
  let url = URL.createObjectURL(blob);
  let a = document.createElement('a');
  a.href = url;
  a.download = 'vuln-sentinel-repair-report.zip';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  showToast('修复报告包已下载');
}

// 将需要在 HTML 内联 onclick 中调用的函数暴露到全局
if (typeof window !== 'undefined') {
  window.copyFixerResult = copyFixerResult;
  window.copyFixedConfig = copyFixedConfig;
  window.downloadNginxConf = downloadNginxConf;
  window.downloadRepairReport = downloadRepairReport;
}

if (typeof window !== 'undefined') {
  setTimeout(loadTicketContextFromStorage, 0);
}


/** 审计工作台的纯函数：用于筛选源码/上线相关结果并计算置信度。 */

const SOURCE_AUDIT_KEYWORDS = [
  '源码', 'source map', '.map', '目录索引', '目录遍历', '路径遍历', '敏感文件', '泄露', '注释',
  'debug', 'backup', '备份', 'phpinfo', '.git', '.env', 'source', 'map', 'index of', 'listing',
  'xss', 'sql 注入', 'sqli', 'ssrf', 'open redirect', '重定向', '登录态', '权限', 'csrf', 'idor', 'traversal',
  '弱口令', '防爆破', 'cookie', 'waf'
];

const SOURCE_EVIDENCE_KEYS = new Set([
  'path', 'url', 'snippet', 'body_hint', 'method', 'detected', 'header', 'value', 'reason', 'impact', 'limitation'
]);

function normalizeText(value) {
  return String(value || '').toLowerCase();
}

function collectText(finding) {
  return [
    finding && finding.name,
    finding && finding.title,
    finding && finding.summary,
    finding && finding.description,
    finding && finding.type,
    finding && finding.category,
    finding && finding.evidence_text,
    finding && finding.evidence_html,
    finding && finding.evidence && JSON.stringify(finding.evidence),
  ].filter(Boolean).join(' ');
}

function hasSourceEvidence(finding) {
  if (!finding || typeof finding !== 'object') return false;
  const evidence = finding.evidence && typeof finding.evidence === 'object' ? finding.evidence : null;
  if (!evidence) return false;
  return Object.keys(evidence).some((key) => SOURCE_EVIDENCE_KEYS.has(key) && evidence[key] !== undefined && evidence[key] !== null && String(evidence[key]).trim() !== '');
}

function evidenceSignalsSourceLeak(finding) {
  if (!finding || typeof finding !== 'object') return false;
  const evidence = finding.evidence && typeof finding.evidence === 'object' ? finding.evidence : null;
  if (!evidence) return false;
  const raw = Object.values(evidence)
    .filter(Boolean)
    .map((v) => String(v).toLowerCase())
    .join(' ');
  if (!raw) return false;
  return [
    'sourcemappingurl',
    'source map',
    '.map',
    '.env',
    '.git',
    '.svn',
    '.bak',
    'backup',
    'dump',
    'phpinfo',
    'index of',
    'directory listing',
    '目录索引',
    '敏感文件',
    '源码泄露',
    '注释',
    'debug',
  ].some((needle) => raw.includes(needle));
}

function inferConfidence(finding) {
  if (!finding || typeof finding !== 'object') return 'low';
  const text = normalizeText(collectText(finding));
  const evidence = finding.evidence && typeof finding.evidence === 'object' ? finding.evidence : null;
  const severity = normalizeText(finding.severity);
  const strongEvidence = evidenceSignalsSourceLeak(finding);
  const hasEvidence = hasSourceEvidence(finding);
  const hasKeyword = SOURCE_AUDIT_KEYWORDS.some((keyword) => text.includes(keyword));
  if (strongEvidence) return 'high';
  if (hasEvidence && hasKeyword) return 'medium';
  if ((severity === 'high' || severity === 'critical') && hasKeyword) return 'medium';
  if (evidence && (normalizeText(evidence.path).includes('.env') || normalizeText(evidence.path).includes('.git') || normalizeText(evidence.path).includes('.map') || normalizeText(evidence.url).includes('.env') || normalizeText(evidence.url).includes('.git') || normalizeText(evidence.url).includes('.map'))) {
    return 'high';
  }
  if (hasKeyword && (text.includes('source') || text.includes('泄露') || text.includes('敏感'))) return 'low';
  return 'low';
}

function isAuditRelevantFinding(finding) {
  if (!finding || typeof finding !== 'object') return false;
  const text = normalizeText(collectText(finding));
  const evidence = finding.evidence && typeof finding.evidence === 'object' ? finding.evidence : null;
  const explicitType = normalizeText(finding.type) || normalizeText(finding.category);
  const hasKeyword = SOURCE_AUDIT_KEYWORDS.some((keyword) => text.includes(keyword));
  const hasEvidence = hasSourceEvidence(finding);
  const strongEvidence = evidenceSignalsSourceLeak(finding);

  if (strongEvidence) return true;
  if (hasEvidence && hasKeyword) return true;
  if ((explicitType === 'exposed' || explicitType === 'exposure' || explicitType === 'sensitive' || explicitType === 'leak') && (hasKeyword || evidence)) return true;
  if ((normalizeText(finding.name).includes('源码') || normalizeText(finding.name).includes('敏感文件') || normalizeText(finding.name).includes('源码泄露')) && hasEvidence) return true;
  return false;
}

function selectAuditFindings(findings) {
  return (Array.isArray(findings) ? findings : [])
    .filter(isAuditRelevantFinding)
    .map((finding) => ({ ...finding, confidence: inferConfidence(finding) }))
    .sort((a, b) => {
      const rank = { high: 3, medium: 2, low: 1 };
      const diff = (rank[b.confidence] || 0) - (rank[a.confidence] || 0);
      if (diff !== 0) return diff;
      const sev = { critical: 4, high: 3, medium: 2, low: 1, info: 0 };
      return (sev[b.severity] || 0) - (sev[a.severity] || 0);
    });
}

function countAuditConfidence(findings) {
  const counts = { high: 0, medium: 0, low: 0 };
  (Array.isArray(findings) ? findings : []).forEach((finding) => {
    const level = String(finding && finding.confidence || 'low').toLowerCase();
    if (counts[level] !== undefined) counts[level] += 1;
  });
  return counts;
}

function buildAuditCoverage() {
  return [
    '源码映射文件',
    '目录索引与备份文件',
    'HTML 注释与调试信息',
    '敏感配置与暴露路径',
    '登录态与权限控制',
    '重定向与路径校验',
    '弱口令与防爆破',
    'XSS / SQL 注入 / SSRF 线索',
    '基础安全响应头',
  ];
}

export { SOURCE_AUDIT_KEYWORDS, hasSourceEvidence, evidenceSignalsSourceLeak, inferConfidence, isAuditRelevantFinding, selectAuditFindings, countAuditConfidence, buildAuditCoverage };

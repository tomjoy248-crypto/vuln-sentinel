import { describe, it, expect, beforeEach } from 'vitest';
import { getRiskSurfaceLabel, groupFindingsByRiskSurface, renderSRCResult } from './result.js';

const sampleFindings = [
  {
    id: 'F-1',
    title: 'API 入口面暴露',
    type: 'api_surface_exposure',
    severity: 'medium',
    evidence: { request: 'GET /', response: 'ok' },
  },
  {
    id: 'F-2',
    title: '敏感路径暴露',
    type: 'backup_exposure',
    severity: 'high',
    evidence: { request: 'GET /', response: 'ok' },
  },
  {
    id: 'F-3',
    title: '缺少 CSP',
    type: 'header_missing',
    severity: 'medium',
    evidence: { request: 'GET /', response: 'ok' },
  },
  {
    id: 'F-4',
    title: '第三方前端资源未固定版本',
    type: 'supply_chain_exposure',
    severity: 'low',
    evidence: { request: 'GET /', response: 'ok' },
  },
];

beforeEach(() => {
  document.body.innerHTML = '<div id="result-content"></div>';
});

describe('result page risk-surface views', () => {
  it('groups findings by stable risk surfaces', () => {
    const grouped = groupFindingsByRiskSurface(sampleFindings);
    expect(grouped.map((group) => group.label)).toEqual([
      '公开暴露面',
      '配置与响应头',
      '组件与供应链',
    ]);
    expect(getRiskSurfaceLabel(sampleFindings[0])).toBe('公开暴露面');
  });

  it('renders the risk-surface overview into the result page', () => {
    renderSRCResult({
      url: 'https://example.com',
      score: 88,
      risk_level: 'High',
      findings: sampleFindings,
      summary: { critical: 0, high: 1, medium: 2, low: 0, info: 0, total: 3, fp_count: 0 },
    });

    const overview = document.querySelector('.src-surface-overview');
    expect(overview).not.toBeNull();
    expect(overview.textContent).toContain('风险面总览');
    expect(overview.textContent).toContain('公开暴露面');
    expect(document.querySelectorAll('.src-list-surface')).toHaveLength(4);
  });

  it('keeps formal report language in the header', () => {
    renderSRCResult({
      url: 'https://example.com',
      score: 88,
      risk_level: 'High',
      scan_id: 12,
      findings: sampleFindings,
      summary: { critical: 0, high: 1, medium: 2, low: 0, info: 0, total: 3, fp_count: 1 },
    });

    const content = document.getElementById('result-content').textContent;
    expect(content).toContain('执行摘要');
    expect(content).toContain('检测摘要');
    expect(content).toContain('管理层关注');
    expect(content).toContain('修复优先级路线');
  });
});

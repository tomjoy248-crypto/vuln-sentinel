import { describe, it, expect } from 'vitest';
import {
  buildAuditCoverage,
  evidenceSignalsSourceLeak,
  inferConfidence,
  isAuditRelevantFinding,
  selectAuditFindings,
  countAuditConfidence,
} from './audit-workbench.js';

describe('audit-workbench helpers', () => {
  it('does not treat keyword-only findings without evidence as audit findings', () => {
    expect(
      isAuditRelevantFinding({
        name: '信息泄露提示',
        summary: '只是一个模糊提示',
        severity: 'low',
      })
    ).toBe(false);
  });

  it('accepts findings with concrete source leak evidence', () => {
    expect(
      isAuditRelevantFinding({
        name: '暴露源码映射文件',
        severity: 'medium',
        evidence: { path: '/assets/app.js.map', snippet: 'sourceMappingURL=app.js.map' },
      })
    ).toBe(true);
  });

  it('detects evidence signals from actual source leak markers', () => {
    expect(
      evidenceSignalsSourceLeak({
        evidence: { snippet: '//# sourceMappingURL=chunk.js.map' },
      })
    ).toBe(true);
  });

  it('assigns higher confidence when evidence is concrete', () => {
    expect(
      inferConfidence({
        name: '敏感文件泄露',
        evidence: { path: '/.env', snippet: 'DB_PASSWORD=secret' },
      })
    ).toBe('high');
  });

  it('sorts stronger evidence first', () => {
    const findings = selectAuditFindings([
      {
        name: '目录索引',
        severity: 'medium',
        evidence: { path: '/static/' },
      },
      {
        name: '暴露源码映射文件',
        severity: 'high',
        evidence: { path: '/assets/app.js.map', snippet: 'sourceMappingURL=app.js.map' },
      },
      {
        name: '无证据提示',
        severity: 'high',
      },
    ]);

    expect(findings).toHaveLength(2);
    expect(findings[0].confidence).toBe('high');
    expect(findings[0].name).toBe('暴露源码映射文件');
    expect(findings[1].confidence).toBe('medium');
  });


  it('counts audit confidence levels', () => {
    expect(countAuditConfidence([
      { confidence: 'high' },
      { confidence: 'medium' },
      { confidence: 'low' },
      { confidence: 'low' },
    ])).toEqual({ high: 1, medium: 1, low: 2 });
  });

  it('keeps the audit coverage list stable', () => {
    expect(buildAuditCoverage()).toEqual([
      '源码映射文件',
      '目录索引与备份文件',
      'HTML 注释与调试信息',
      '敏感配置与暴露路径',
      '登录态与权限控制',
      '重定向与路径校验',
      '弱口令与防爆破',
      'XSS / SQL 注入 / SSRF 线索',
      '基础安全响应头',
    ]);
  });
});

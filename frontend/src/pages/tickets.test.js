import { describe, it, expect } from 'vitest';
import { buildBatchTicketSummary, buildTicketClosureSummary } from './tickets.js';

describe('ticket closure summary', () => {
  it('builds a fixed-state closure summary', () => {
    const summary = buildTicketClosureSummary(
      { status: 'fixed', severity: 'high' },
      [
        { label: '发现漏洞', status: 'done', time: '2026-08-31 10:00:00' },
        { label: '确认修复', status: 'done', time: '2026-08-31 10:10:00' },
        { label: '应用修复', status: 'done', time: '2026-08-31 10:30:00' },
        { label: '复测验证', status: 'done', time: '2026-08-31 10:40:00' },
        { label: '闭环完成', status: 'done', time: '2026-08-31 10:45:00' }
      ]
    );

    expect(summary.headline).toContain('已完成修复闭环');
    expect(summary.progressText).toBe('已完成 5/5 个闭环阶段');
    expect(summary.latestTime).toBe('2026-08-31 10:45:00');
  });

  it('builds a failed-state closure summary with blocker hint', () => {
    const summary = buildTicketClosureSummary(
      { status: 'failed', severity: 'medium' },
      [
        { label: '发现漏洞', status: 'done', time: '2026-08-31 10:00:00' },
        { label: '确认修复', status: 'done', time: '2026-08-31 10:10:00' },
        { label: '修复失败', status: 'failed', time: '2026-08-31 11:00:00' }
      ]
    );

    expect(summary.headline).toContain('未通过验证');
    expect(summary.failedLabel).toBe('修复失败');
    expect(summary.nextStep).toContain('二次修复');
  });

  it('builds exportable summaries for multiple tickets', () => {
    const text = buildBatchTicketSummary([
      { id: 1, finding_name: '缺少 HSTS', severity: 'high', status: 'confirmed', url: 'https://example.com' },
      { id: 2, finding_name: '后台页面匿名可访问', severity: 'critical', status: 'fixed', url: 'https://example.com/admin' }
    ]);

    expect(text).toContain('工单 #1');
    expect(text).toContain('工单 #2');
    expect(text).toContain('闭环摘要');
    expect(text).toContain('下一步');
  });
});

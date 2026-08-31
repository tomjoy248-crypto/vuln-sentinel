import { describe, it, expect } from 'vitest';
import { APP_TEMPLATE } from './templates.js';

describe('APP_TEMPLATE', () => {
  it('renders a workbench-style home page with the scan entry first', () => {
    expect(APP_TEMPLATE).toContain('id="page-home"');
    expect(APP_TEMPLATE).toContain('id="scan-section"');
    expect(APP_TEMPLATE).toContain('id="scan-url"');
    expect(APP_TEMPLATE).toContain('id="scan-btn-step1"');
    expect(APP_TEMPLATE).toContain('id="page-result"');
  });

  it('keeps the scan entry before the result page in the template', () => {
    expect(APP_TEMPLATE.indexOf('id="scan-section"')).toBeLessThan(APP_TEMPLATE.indexOf('id="page-result"'));
  });

  it('uses formal product copy on the home and result pages', () => {
    expect(APP_TEMPLATE).toContain('Vuln Sentinel Web 安全检测平台');
    expect(APP_TEMPLATE).toContain('公开样例报告');
    expect(APP_TEMPLATE).toContain('查看风险发现、证据详情与整改建议');
  });
});

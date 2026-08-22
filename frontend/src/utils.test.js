import { describe, it, expect, beforeEach } from 'vitest';
import {
  safeGetElement,
  safeSetText,
  safeSetHtml,
  safeSetValue,
  safeSetDisplay,
  escapeHtml,
  escapeAttr,
  getHost,
  getScoreColor,
  getScoreGradient,
  getRiskClass,
  getRiskColor,
  formatDate,
  cssEscape,
  extractError,
  isPaymentRequired,
  paymentRequiredMessage,
  friendlyError,
  setButtonLoading,
  renderPagination,
  renderEvidence,
  copyToClipboard,
  EVIDENCE_LABELS,
  EVIDENCE_ORDER,
} from './utils.js';

describe('escapeHtml', () => {
  it('escapes <, > and &', () => {
    expect(escapeHtml('<script>alert("x")</script>')).toBe(
      '&lt;script&gt;alert("x")&lt;/script&gt;'
    );
    expect(escapeHtml('a & b')).toBe('a &amp; b');
  });

  it('returns empty string for null and undefined', () => {
    expect(escapeHtml(null)).toBe('');
    expect(escapeHtml(undefined)).toBe('');
  });

  it('coerces non-strings to strings', () => {
    expect(escapeHtml(42)).toBe('42');
  });
});

describe('escapeAttr', () => {
  it('escapes single and double quotes', () => {
    expect(escapeAttr('a"b\'c')).toBe('a&quot;b&#39;c');
  });

  it('returns empty string for null/undefined', () => {
    expect(escapeAttr(null)).toBe('');
    expect(escapeAttr(undefined)).toBe('');
  });

  it('coerces numbers to strings', () => {
    expect(escapeAttr(123)).toBe('123');
  });
});

describe('getHost', () => {
  it('extracts hostname from a bare host', () => {
    expect(getHost('example.com')).toBe('example.com');
  });

  it('extracts hostname from a full url', () => {
    expect(getHost('https://a.b.com/path?q=1')).toBe('a.b.com');
  });

  it('strips the port', () => {
    expect(getHost('http://example.com:8080/x')).toBe('example.com');
  });
});

describe('getScoreColor', () => {
  it('returns green for high scores', () => {
    expect(getScoreColor(80)).toBe('#73c990');
    expect(getScoreColor(75)).toBe('#73c990');
  });

  it('returns orange for medium scores', () => {
    expect(getScoreColor(60)).toBe('#f0a732');
    expect(getScoreColor(50)).toBe('#f0a732');
  });

  it('returns red for low scores and invalid input', () => {
    expect(getScoreColor(30)).toBe('#c75450');
    expect(getScoreColor(49)).toBe('#c75450');
    expect(getScoreColor('abc')).toBe('#c75450');
  });
});

describe('getScoreGradient', () => {
  it('builds a green gradient for high scores', () => {
    expect(getScoreGradient(80)).toBe('conic-gradient(#73c990 0% 80%, #334155 80% 100%)');
  });

  it('builds an orange gradient for medium scores', () => {
    expect(getScoreGradient(60)).toBe('conic-gradient(#f0a732 0% 60%, #334155 60% 100%)');
  });

  it('builds a red gradient for low scores', () => {
    expect(getScoreGradient(30)).toBe('conic-gradient(#c75450 0% 30%, #334155 30% 100%)');
  });

  it('clamps scores to the 0-100 range', () => {
    expect(getScoreGradient(150)).toBe('conic-gradient(#73c990 0% 100%, #334155 100% 100%)');
    expect(getScoreGradient(-5)).toBe('conic-gradient(#c75450 0% 0%, #334155 0% 100%)');
  });
});

describe('getRiskClass', () => {
  it('maps high risk labels', () => {
    expect(getRiskClass('高风险')).toBe('high');
    expect(getRiskClass('high')).toBe('high');
  });

  it('maps medium risk labels', () => {
    expect(getRiskClass('中风险')).toBe('medium');
    expect(getRiskClass('medium')).toBe('medium');
  });

  it('defaults to low', () => {
    expect(getRiskClass('低风险')).toBe('low');
    expect(getRiskClass('whatever')).toBe('low');
  });
});

describe('getRiskColor', () => {
  it('returns neutral color for empty level', () => {
    expect(getRiskColor('')).toBe('var(--text-secondary)');
    expect(getRiskColor(null)).toBe('var(--text-secondary)');
  });

  it('returns red for high/critical', () => {
    expect(getRiskColor('高风险')).toBe('#c75450');
    expect(getRiskColor('critical')).toBe('#c75450');
  });

  it('returns orange for medium', () => {
    expect(getRiskColor('中风险')).toBe('#f0a732');
    expect(getRiskColor('medium')).toBe('#f0a732');
  });

  it('returns green for low', () => {
    expect(getRiskColor('低风险')).toBe('#16a34a');
    expect(getRiskColor('low')).toBe('#16a34a');
  });

  it('returns neutral color for unknown levels', () => {
    expect(getRiskColor('info')).toBe('var(--text-secondary)');
  });
});

describe('formatDate', () => {
  it('returns "-" for empty input', () => {
    expect(formatDate('')).toBe('-');
    expect(formatDate(null)).toBe('-');
  });

  it('returns the input for unparseable dates', () => {
    expect(formatDate('not-a-date')).toBe('not-a-date');
  });

  it('formats valid dates as YYYY-MM-DD HH:mm', () => {
    const result = formatDate('2024-01-15T10:30:00Z');
    expect(result).toMatch(/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$/);
  });
});

describe('cssEscape', () => {
  it('leaves simple identifiers untouched', () => {
    expect(cssEscape('simple')).toBe('simple');
  });

  it('escapes special characters', () => {
    expect(cssEscape('a.b')).not.toBe('a.b');
  });
});

describe('extractError', () => {
  it('returns default message for empty data', () => {
    expect(extractError(null)).toBe('未知错误');
    expect(extractError(undefined)).toBe('未知错误');
  });

  it('returns the error field when present', () => {
    expect(extractError({ error: 'oops' })).toBe('oops');
  });

  it('falls back to detail then message', () => {
    expect(extractError({ detail: 'det' })).toBe('det');
    expect(extractError({ message: 'msg' })).toBe('msg');
  });

  it('returns a generic message when no field matches', () => {
    expect(extractError({})).toBe('请求失败');
  });

  it('appends guidance for restricted code', () => {
    expect(extractError({ error: 'denied', restricted_code: 'restricted' })).toBe(
      'denied（该目标类型受限，请确认您拥有合法授权后再扫描）'
    );
  });

  it('appends guidance for ownership_required', () => {
    expect(extractError({ restricted_code: 'ownership_required' })).toBe(
      '请求失败，请先完成域名归属验证。'
    );
  });

  it('appends guidance for unauthorized', () => {
    expect(extractError({ restricted_code: 'unauthorized' })).toBe(
      '请求失败（请先确认您有权扫描该目标）'
    );
  });
});

describe('isPaymentRequired', () => {
  it('is true only with 402 status and PAYMENT_REQUIRED code', () => {
    expect(isPaymentRequired({ _status: 402, code: 'PAYMENT_REQUIRED' })).toBe(true);
  });

  it('is falsy otherwise', () => {
    expect(isPaymentRequired({ _status: 402 })).toBeFalsy();
    expect(isPaymentRequired({ _status: 200, code: 'PAYMENT_REQUIRED' })).toBeFalsy();
    expect(isPaymentRequired({})).toBeFalsy();
    expect(isPaymentRequired(null)).toBeFalsy();
  });
});

describe('paymentRequiredMessage', () => {
  it('returns the message when payment required', () => {
    expect(
      paymentRequiredMessage({ _status: 402, code: 'PAYMENT_REQUIRED', message: 'need credits' })
    ).toBe('need credits');
  });

  it('returns a default message when no message is provided', () => {
    expect(paymentRequiredMessage({ _status: 402, code: 'PAYMENT_REQUIRED' })).toBe(
      '额度不足，请充值后再试'
    );
  });

  it('returns empty string when not payment required', () => {
    expect(paymentRequiredMessage({ _status: 200 })).toBe('');
    expect(paymentRequiredMessage(null)).toBe('');
  });
});

describe('friendlyError', () => {
  it('detects timeout errors', () => {
    expect(friendlyError({ message: 'Request timeout' })).toBe('请求超时，请检查网络连接或稍后重试');
  });

  it('detects network errors', () => {
    expect(friendlyError({ message: 'network error' })).toBe(
      '网络连接异常，请确认本地后端已启动，或检查防火墙是否拦截了 127.0.0.1:8011'
    );
  });

  it('detects 403 errors', () => {
    expect(friendlyError({ message: '403 Forbidden' })).toBe('请求被拒绝，请检查权限或目标授权状态');
  });

  it('detects 404 errors', () => {
    expect(friendlyError({ message: '404 not found' })).toBe(
      '请求的资源不存在，请确认接口或页面地址是否正确'
    );
  });

  it('detects server errors', () => {
    expect(friendlyError({ message: '500 server error' })).toBe(
      '服务器暂时不可用，请稍后重试，或重启本地后端后再试'
    );
  });

  it('detects auth errors', () => {
    expect(friendlyError({ message: 'unauthorized 401' })).toBe('登录状态已过期，请重新登录');
  });

  it('returns the original message when no pattern matches', () => {
    expect(friendlyError({ message: 'something else' })).toBe('something else');
  });

  it('handles string errors', () => {
    expect(friendlyError('timeout occurred')).toBe('请求超时，请检查网络连接或稍后重试');
  });
});

describe('DOM helpers', () => {
  beforeEach(() => {
    document.body.innerHTML = '';
  });

  it('safeGetElement returns null when missing', () => {
    expect(safeGetElement('missing')).toBeNull();
  });

  it('safeGetElement returns the element when present', () => {
    const el = document.createElement('div');
    el.id = 'foo';
    document.body.appendChild(el);
    expect(safeGetElement('foo')).toBe(el);
  });

  it('safeSetText updates textContent', () => {
    const el = document.createElement('div');
    el.id = 'foo';
    document.body.appendChild(el);
    safeSetText('foo', 'hello');
    expect(el.textContent).toBe('hello');
  });

  it('safeSetHtml updates innerHTML', () => {
    const el = document.createElement('div');
    el.id = 'foo';
    document.body.appendChild(el);
    safeSetHtml('foo', '<b>x</b>');
    expect(el.innerHTML).toBe('<b>x</b>');
  });

  it('safeSetValue updates input value', () => {
    const input = document.createElement('input');
    input.id = 'foo';
    document.body.appendChild(input);
    safeSetValue('foo', 'abc');
    expect(input.value).toBe('abc');
  });

  it('safeSetDisplay updates style.display', () => {
    const el = document.createElement('div');
    el.id = 'foo';
    document.body.appendChild(el);
    safeSetDisplay('foo', 'none');
    expect(el.style.display).toBe('none');
  });

  it('safe* helpers do not throw when the element is missing', () => {
    expect(() => safeSetText('missing', 'x')).not.toThrow();
    expect(() => safeSetHtml('missing', '<b></b>')).not.toThrow();
    expect(() => safeSetValue('missing', 'x')).not.toThrow();
    expect(() => safeSetDisplay('missing', 'none')).not.toThrow();
  });
});

describe('setButtonLoading', () => {
  beforeEach(() => {
    document.body.innerHTML = '';
  });

  it('toggles loading state and restores original text', () => {
    const btn = document.createElement('button');
    btn.id = 'btn';
    btn.textContent = 'Submit';
    document.body.appendChild(btn);

    setButtonLoading('btn', true);
    expect(btn.textContent).toBe('处理中...');
    expect(btn.disabled).toBe(true);

    setButtonLoading('btn', false);
    expect(btn.textContent).toBe('Submit');
    expect(btn.disabled).toBe(false);
  });

  it('does not throw for a missing button', () => {
    expect(() => setButtonLoading('missing', true)).not.toThrow();
  });
});

describe('renderPagination', () => {
  beforeEach(() => {
    document.body.innerHTML = '';
  });

  it('renders nothing when totalPages <= 1', () => {
    const container = document.createElement('div');
    container.id = 'pager';
    document.body.appendChild(container);
    renderPagination('pager', 1, 1, () => {});
    expect(container.innerHTML).toBe('');
  });

  it('renders page buttons and marks the current page active', () => {
    const container = document.createElement('div');
    container.id = 'pager';
    document.body.appendChild(container);
    renderPagination('pager', 2, 3, () => {});
    const active = container.querySelector('.page-btn.active');
    expect(active).not.toBeNull();
    expect(active.textContent).toBe('2');
  });

  it('calls onPageChange when a page button is clicked', () => {
    const container = document.createElement('div');
    container.id = 'pager';
    document.body.appendChild(container);
    let called = null;
    renderPagination('pager', 1, 3, (p) => {
      called = p;
    });
    const buttons = container.querySelectorAll('.page-btn');
    const target = Array.from(buttons).find((b) => b.dataset.page === '2');
    expect(target).toBeDefined();
    target.click();
    expect(called).toBe(2);
  });
});

describe('renderEvidence', () => {
  it('returns empty string for null/undefined/non-object', () => {
    expect(renderEvidence(null)).toBe('');
    expect(renderEvidence(undefined)).toBe('');
    expect(renderEvidence('str')).toBe('');
  });

  it('returns empty string for an empty object', () => {
    expect(renderEvidence({})).toBe('');
  });

  it('renders the detected status', () => {
    expect(renderEvidence({ detected: true })).toContain('已检测到');
    expect(renderEvidence({ detected: false })).toContain('未检测到');
  });

  it('renders the reason label and value', () => {
    const html = renderEvidence({ reason: 'because' });
    expect(html).toContain('判断依据');
    expect(html).toContain('because');
  });

  it('escapes payload content', () => {
    const html = renderEvidence({ payload: '<img src=x>' });
    expect(html).toContain('&lt;img src=x&gt;');
    expect(html).not.toContain('<img src=x>');
  });
});

describe('evidence constants', () => {
  it('EVIDENCE_LABELS maps known keys to labels', () => {
    expect(EVIDENCE_LABELS.detected).toBe('检测结果');
    expect(EVIDENCE_LABELS.payload).toBe('测试 Payload');
  });

  it('EVIDENCE_ORDER is an array starting with detected', () => {
    expect(Array.isArray(EVIDENCE_ORDER)).toBe(true);
    expect(EVIDENCE_ORDER[0]).toBe('detected');
  });
});

describe('copyToClipboard', () => {
  it('writes text via navigator.clipboard when available', async () => {
    let captured = null;
    const fakeClipboard = {
      writeText: (t) => {
        captured = t;
        return Promise.resolve();
      },
    };
    const hadOwn = Object.prototype.hasOwnProperty.call(navigator, 'clipboard');
    const originalDesc = hadOwn
      ? Object.getOwnPropertyDescriptor(navigator, 'clipboard')
      : null;
    Object.defineProperty(navigator, 'clipboard', {
      value: fakeClipboard,
      configurable: true,
      writable: true,
    });
    try {
      await copyToClipboard('hello world');
      expect(captured).toBe('hello world');
    } finally {
      if (originalDesc) {
        Object.defineProperty(navigator, 'clipboard', originalDesc);
      } else {
        delete navigator.clipboard;
      }
    }
  });
});

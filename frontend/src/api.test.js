import { beforeEach, describe, expect, it, vi } from 'vitest';
import { API_BASE, authFetch, parseJsonResponse } from './api.js';

describe('API_BASE', () => {
  it('should be an empty string for relative paths', () => {
    expect(API_BASE).toBe('');
  });
});

beforeEach(() => {
  vi.restoreAllMocks();
});

describe('authFetch', () => {
  it('retries network errors once before failing', async () => {
    const fetchMock = vi.fn().mockRejectedValue(new Error('network down'));
    vi.stubGlobal('fetch', fetchMock);
    await expect(authFetch('/api/login', { method: 'POST', body: '{}' })).rejects.toThrow('无法连接扫描服务，请确认本地后端已启动');
    expect(fetchMock.mock.calls.length).toBeGreaterThan(1);
  });
});

describe('parseJsonResponse', () => {
  it('turns an HTML fallback into an actionable local-service error', async () => {
    const response = new Response('<!DOCTYPE html><html><body>app</body></html>', {
      status: 200,
      headers: { 'content-type': 'text/html; charset=utf-8' },
    });

    await expect(parseJsonResponse(response)).rejects.toThrow(
      '本地后端没有正确响应，请确认安装包内本地服务已启动后重试',
    );
  });

  it('parses valid JSON responses', async () => {
    const response = new Response(JSON.stringify({ token: 'test-token' }), {
      status: 200,
      headers: { 'content-type': 'application/json' },
    });

    await expect(parseJsonResponse(response)).resolves.toEqual({ token: 'test-token' });
  });
});

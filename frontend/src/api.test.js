import { beforeEach, describe, expect, it, vi } from 'vitest';
import { API_BASE, authFetch } from './api.js';

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

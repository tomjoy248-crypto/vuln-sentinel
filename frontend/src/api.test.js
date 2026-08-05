import { describe, it, expect } from 'vitest';
import { API_BASE } from './api.js';

describe('API_BASE', () => {
  it('should be an empty string for relative paths', () => {
    expect(API_BASE).toBe('');
  });
});

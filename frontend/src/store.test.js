import { describe, it, expect } from 'vitest';
import { createStore, appStore } from './store.js';

describe('createStore', () => {
  it('exposes getState, setState and subscribe', () => {
    const store = createStore({ count: 0 });
    expect(typeof store.getState).toBe('function');
    expect(typeof store.setState).toBe('function');
    expect(typeof store.subscribe).toBe('function');
  });

  it('getState returns the initial state', () => {
    const store = createStore({ count: 0, name: 'a' });
    expect(store.getState()).toEqual({ count: 0, name: 'a' });
  });

  it('does not mutate the initial state object passed in', () => {
    const initial = { count: 0 };
    const store = createStore(initial);
    store.setState({ count: 5 });
    expect(initial.count).toBe(0);
    expect(store.getState().count).toBe(5);
  });

  it('setState merges partial updates', () => {
    const store = createStore({ count: 0, name: 'a' });
    store.setState({ count: 10 });
    expect(store.getState()).toEqual({ count: 10, name: 'a' });
  });

  it('notifies subscribers with the new state', () => {
    const store = createStore({ count: 0 });
    let received = null;
    store.subscribe((state) => {
      received = state;
    });
    store.setState({ count: 7 });
    expect(received).toEqual({ count: 7 });
  });

  it('subscribe returns an unsubscribe function', () => {
    const store = createStore({ count: 0 });
    let calls = 0;
    const unsubscribe = store.subscribe(() => {
      calls++;
    });
    expect(typeof unsubscribe).toBe('function');
    store.setState({ count: 1 });
    expect(calls).toBe(1);
    unsubscribe();
    store.setState({ count: 2 });
    expect(calls).toBe(1);
  });

  it('supports multiple subscribers', () => {
    const store = createStore({ count: 0 });
    let a = 0;
    let b = 0;
    store.subscribe(() => {
      a++;
    });
    store.subscribe(() => {
      b++;
    });
    store.setState({ count: 1 });
    expect(a).toBe(1);
    expect(b).toBe(1);
  });

  it('isolates subscriber errors so other subscribers still run', () => {
    const store = createStore({ count: 0 });
    const originalError = console.error;
    console.error = () => {};
    let secondCalled = false;
    store.subscribe(() => {
      throw new Error('boom');
    });
    store.subscribe(() => {
      secondCalled = true;
    });
    store.setState({ count: 1 });
    console.error = originalError;
    expect(secondCalled).toBe(true);
  });
});

describe('appStore', () => {
  it('is initialized with tickets, ticketFilter and user', () => {
    const state = appStore.getState();
    expect(state).toHaveProperty('tickets');
    expect(state).toHaveProperty('ticketFilter');
    expect(state).toHaveProperty('user');
    expect(Array.isArray(state.tickets)).toBe(true);
    expect(state.ticketFilter).toBe('pending');
    expect(state.user).toBeNull();
  });

  it('supports updating its state via setState', () => {
    const originalFilter = appStore.getState().ticketFilter;
    appStore.setState({ ticketFilter: 'done' });
    expect(appStore.getState().ticketFilter).toBe('done');
    appStore.setState({ ticketFilter: originalFilter });
    expect(appStore.getState().ticketFilter).toBe(originalFilter);
  });
});

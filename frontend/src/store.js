/**
 * Tiny reactive store.
 *
 * createStore(initialState) returns:
 *   - getState()
 *   - setState(partialUpdate)
 *   - subscribe(callback)
 */
export function createStore(initialState) {
  let state = Object.assign({}, initialState);
  const listeners = new Set();

  return {
    getState() {
      return state;
    },
    setState(update) {
      state = Object.assign({}, state, update);
      listeners.forEach(function (cb) {
        try { cb(state); } catch (e) { console.error('store subscriber error:', e); }
      });
    },
    subscribe(callback) {
      listeners.add(callback);
      return function unsubscribe() {
        listeners.delete(callback);
      };
    }
  };
}

export const appStore = createStore({
  tickets: [],
  ticketFilter: 'pending',
  user: null
});

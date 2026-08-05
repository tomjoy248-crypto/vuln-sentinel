import { appStore } from '../store.js';
import {
  listTickets,
  getTicket,
  updateTicket,
  deleteTicket as apiDeleteTicket,
  apiPost,
  apiGet
} from '../api.js';

export async function loadTickets() {
  const data = await listTickets();
  const tickets = (data && data.tickets) ? data.tickets : [];
  appStore.setState({ tickets: tickets });
  return data;
}

export function setFilter(status) {
  appStore.setState({ ticketFilter: status });
}

export function getFilteredTickets() {
  const state = appStore.getState();
  return state.tickets.filter(function (t) { return t.status === state.ticketFilter; });
}

export function getTicketById(id) {
  const state = appStore.getState();
  return state.tickets.find(function (t) { return t.id === id; }) || null;
}

export async function updateTicketStatus(id, status) {
  const result = await updateTicket(id, { status: status });
  const state = appStore.getState();
  const tickets = state.tickets.map(function (t) {
    return t.id === id ? Object.assign({}, t, { status: status }) : t;
  });
  appStore.setState({ tickets: tickets });
  return result;
}

export async function updateTicketNotes(id, notes) {
  const result = await updateTicket(id, { notes: notes });
  const state = appStore.getState();
  const tickets = state.tickets.map(function (t) {
    return t.id === id ? Object.assign({}, t, { notes: notes }) : t;
  });
  appStore.setState({ tickets: tickets });
  return result;
}

export async function deleteTicket(id) {
  const result = await apiDeleteTicket(id);
  const state = appStore.getState();
  const tickets = state.tickets.filter(function (t) { return t.id !== id; });
  appStore.setState({ tickets: tickets });
  return result;
}

export async function batchUpdate(ids, status) {
  const results = [];
  for (let i = 0; i < ids.length; i++) {
    results.push(await updateTicket(ids[i], { status: status }));
  }
  const state = appStore.getState();
  const tickets = state.tickets.map(function (t) {
    return ids.indexOf(t.id) !== -1 ? Object.assign({}, t, { status: status }) : t;
  });
  appStore.setState({ tickets: tickets });
  return results;
}

export async function batchDelete(ids) {
  const results = [];
  for (let i = 0; i < ids.length; i++) {
    results.push(await apiDeleteTicket(ids[i]));
  }
  const state = appStore.getState();
  const tickets = state.tickets.filter(function (t) { return ids.indexOf(t.id) === -1; });
  appStore.setState({ tickets: tickets });
  return results;
}

export async function verifyTicket(id) {
  const result = await apiPost('/api/fix-tickets/' + id + '/verify', { rescan: true });
  // Verification changes server-side state; callers typically reload afterwards.
  appStore.setState({ lastVerifiedAt: Date.now() });
  return result;
}

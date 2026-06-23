/* ============================================================
   Stay or Leave — API client
   Thin wrapper over fetch(): attaches the JWT, parses JSON,
   and normalizes errors so callers can just `await api.get(...)`.
   ============================================================ */

const API_BASE = (() => {
  // Same-origin by default; override by setting window.STAY_OR_LEAVE_API_BASE
  // before this script loads if the backend is hosted elsewhere.
  return window.STAY_OR_LEAVE_API_BASE || '/api';
})();

class ApiError extends Error {
  constructor(message, status, fields) {
    super(message);
    this.status = status;
    this.fields = fields || [];
  }
}

function getAccessToken() {
  return localStorage.getItem('sol_access_token');
}

function getRefreshToken() {
  return localStorage.getItem('sol_refresh_token');
}

function setTokens({ access_token, refresh_token } = {}) {
  if (access_token) localStorage.setItem('sol_access_token', access_token);
  if (refresh_token) localStorage.setItem('sol_refresh_token', refresh_token);
}

function clearTokens() {
  localStorage.removeItem('sol_access_token');
  localStorage.removeItem('sol_refresh_token');
  localStorage.removeItem('sol_user');
}

function getCachedUser() {
  try {
    const raw = localStorage.getItem('sol_user');
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function setCachedUser(user) {
  if (user) localStorage.setItem('sol_user', JSON.stringify(user));
}

async function request(method, path, { body, isForm, retry = true } = {}) {
  const headers = {};
  const token = getAccessToken();
  if (token) headers['Authorization'] = `Bearer ${token}`;
  if (!isForm) headers['Content-Type'] = 'application/json';

  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: isForm ? body : body ? JSON.stringify(body) : undefined,
  });

  // Access token expired — try a silent refresh once, then retry the call.
  if (res.status === 401 && retry && getRefreshToken() && path !== '/auth/refresh') {
    const refreshed = await tryRefresh();
    if (refreshed) {
      return request(method, path, { body, isForm, retry: false });
    }
    clearTokens();
  }

  let data = null;
  try {
    data = await res.json();
  } catch {
    data = null;
  }

  if (!res.ok) {
    throw new ApiError(
      (data && data.error) || `Request failed (${res.status})`,
      res.status,
      data && data.fields
    );
  }

  return data;
}

async function tryRefresh() {
  try {
    const res = await fetch(`${API_BASE}/auth/refresh`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${getRefreshToken()}` },
    });
    if (!res.ok) return false;
    const data = await res.json();
    setTokens({ access_token: data.access_token });
    return true;
  } catch {
    return false;
  }
}

const api = {
  get: (path) => request('GET', path),
  post: (path, body, opts) => request('POST', path, { body, ...opts }),
  put: (path, body) => request('PUT', path, { body }),
  del: (path) => request('DELETE', path),
  postForm: (path, formData) => request('POST', path, { body: formData, isForm: true }),
};

window.SOL = window.SOL || {};
window.SOL.api = api;
window.SOL.ApiError = ApiError;
window.SOL.auth = { getAccessToken, getRefreshToken, setTokens, clearTokens, getCachedUser, setCachedUser };

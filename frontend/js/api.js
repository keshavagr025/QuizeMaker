const API_BASE = "/api";

function getToken() {
  return localStorage.getItem("qf_token");
}

function setAuth(token, name, email) {
  localStorage.setItem("qf_token", token);
  localStorage.setItem("qf_name", name);
  localStorage.setItem("qf_email", email);
}

function clearAuth() {
  localStorage.removeItem("qf_token");
  localStorage.removeItem("qf_name");
  localStorage.removeItem("qf_email");
}

function isLoggedIn() {
  return !!getToken();
}

function getUserName() {
  return localStorage.getItem("qf_name") || "User";
}

async function apiFetch(path, options = {}) {
  const token = getToken();
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(API_BASE + path, { ...options, headers });
  const data = await res.json();

  if (res.status === 401) {
    clearAuth();
    window.location.href = "/login.html";
    return;
  }

  return { ok: res.ok, status: res.status, data };
}

async function apiUpload(path, formData) {
  const token = getToken();
  const headers = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(API_BASE + path, { method: "POST", headers, body: formData });
  const data = await res.json();
  return { ok: res.ok, status: res.status, data };
}

function requireAuth() {
  if (!isLoggedIn()) {
    window.location.href = "/login.html";
    return false;
  }
  return true;
}

function redirectIfAuth() {
  if (isLoggedIn()) {
    window.location.href = "/dashboard.html";
  }
}

function showAlert(id, msg, type = "error") {
  const el = document.getElementById(id);
  if (!el) return;
  el.className = `alert alert-${type}`;
  el.textContent = msg;
  el.style.display = "block";
  setTimeout(() => { el.style.display = "none"; }, 5000);
}

function setLoading(btnId, loading, text = "") {
  const btn = document.getElementById(btnId);
  if (!btn) return;
  btn.disabled = loading;
  if (loading) {
    btn.dataset.originalText = btn.innerHTML;
    btn.innerHTML = `<span class="spinner"></span> ${text || "Loading..."}`;
  } else {
    btn.innerHTML = btn.dataset.originalText || text;
  }
}

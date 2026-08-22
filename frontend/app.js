const DEFAULT_API_BASE = defaultApiBase();
const STORAGE_KEY = "ryourl.frontend.session";

const state = {
    apiBase: DEFAULT_API_BASE,
    user: null,
    access: null,
    refresh: null,
};

function defaultApiBase() {
    const hostname = window.location.hostname || "localhost";
    return `http://${hostname}:8003/api`;
}

const els = {};

document.addEventListener("DOMContentLoaded", () => {
    bindElements();
    loadState();
    bindEvents();
    renderSession();
    checkConnection();
});

function bindElements() {
    [
        "apiBaseInput",
        "saveApiBase",
        "connectionStatus",
        "sessionUser",
        "refreshButton",
        "logoutButton",
        "notice",
        "noticeTitle",
        "noticeContent",
        "closeNotice",
        "createUrlForm",
        "originUrl",
        "expireDate",
        "createSubmit",
        "createResult",
        "lookupUrlForm",
        "lookupShortString",
        "lookupSubmit",
        "lookupResult",
        "loginForm",
        "loginUsername",
        "loginPassword",
        "loginSubmit",
        "registerForm",
        "registerUsername",
        "registerPassword",
        "registerSubmit",
        "customUrlForm",
        "customOriginUrl",
        "customShortString",
        "customExpireDate",
        "customSubmit",
        "refreshMyUrls",
        "myUrlsBody",
        "myUrlsEmpty",
        "adminPanel",
        "adminLoadUrls",
        "adminLoadUsers",
        "adminExpireUrls",
        "adminOutput",
    ].forEach((id) => {
        els[id] = document.getElementById(id);
    });
}

function bindEvents() {
    els.saveApiBase.addEventListener("click", () => {
        state.apiBase = normalizeApiBase(els.apiBaseInput.value);
        saveState();
        showNotice("positive", "API 已更新", state.apiBase);
        checkConnection();
    });

    els.closeNotice.addEventListener("click", hideNotice);
    els.logoutButton.addEventListener("click", logout);
    els.refreshButton.addEventListener("click", refreshAccessToken);

    els.createUrlForm.addEventListener("submit", handleCreateUrl);
    els.lookupUrlForm.addEventListener("submit", handleLookupUrl);
    els.loginForm.addEventListener("submit", handleLogin);
    els.registerForm.addEventListener("submit", handleRegister);
    els.customUrlForm.addEventListener("submit", handleCustomUrl);
    els.refreshMyUrls.addEventListener("click", loadMyUrls);

    els.myUrlsBody.addEventListener("click", handleMyUrlAction);
    els.adminLoadUrls.addEventListener("click", loadAdminUrls);
    els.adminLoadUsers.addEventListener("click", loadAdminUsers);
    els.adminExpireUrls.addEventListener("click", deleteExpiredUrls);
    els.adminOutput.addEventListener("click", handleAdminAction);
}

function loadState() {
    try {
        const saved = JSON.parse(localStorage.getItem(STORAGE_KEY));
        if (saved) {
            state.apiBase = saved.apiBase || DEFAULT_API_BASE;
            state.user = saved.user || null;
            state.access = saved.access || null;
            state.refresh = saved.refresh || null;
        }
    } catch {
        localStorage.removeItem(STORAGE_KEY);
    }
    els.apiBaseInput.value = state.apiBase;
}

function saveState() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

function normalizeApiBase(value) {
    const base = (value || DEFAULT_API_BASE).trim();
    return base.replace(/\/+$/, "");
}

function isAuthenticated() {
    return Boolean(state.access && state.user);
}

function isAdmin() {
    return state.user?.user_type === 2;
}

async function apiFetch(path, options = {}) {
    const { method = "GET", body, auth = false, query } = options;
    const url = new URL(`${state.apiBase}${path}`);
    if (query) {
        Object.entries(query).forEach(([key, value]) => {
            if (value !== undefined && value !== null && value !== "") {
                url.searchParams.set(key, value);
            }
        });
    }

    const headers = { Accept: "application/json" };
    if (body !== undefined) {
        headers["Content-Type"] = "application/json";
    }
    if (auth) {
        if (!state.access) {
            throw new Error("請先登入。");
        }
        headers.Authorization = `Bearer ${state.access}`;
    }

    const response = await fetch(url, {
        method,
        headers,
        body: body === undefined ? undefined : JSON.stringify(body),
    });

    if (response.status === 204) {
        return null;
    }

    const text = await response.text();
    let payload = null;
    if (text) {
        try {
            payload = JSON.parse(text);
        } catch {
            payload = { detail: text };
        }
    }

    if (!response.ok) {
        throw new Error(payload?.detail || `HTTP ${response.status}`);
    }

    return payload;
}

async function checkConnection() {
    setConnection("muted");
    try {
        await apiFetch("/openapi.json");
        setConnection("ok");
    } catch (error) {
        setConnection("error");
        showNotice("negative", "無法連線到 API", error.message);
    }
}

function setConnection(status) {
    els.connectionStatus.classList.remove("is-muted", "is-ok", "is-error");
    els.connectionStatus.classList.add(`is-${status}`);
}

async function handleCreateUrl(event) {
    event.preventDefault();
    await runWithButton(els.createSubmit, async () => {
        const payload = buildCreatePayload(els.originUrl.value, els.expireDate.value);
        const data = await apiFetch("/short-url/short", {
            method: "POST",
            body: payload,
        });
        els.createResult.classList.remove("is-empty");
        els.createResult.innerHTML = renderUrlDetails(data);
        showNotice("positive", "短網址已建立", data.short_url);
        if (isAuthenticated()) {
            loadMyUrls();
        }
    });
}

async function handleLookupUrl(event) {
    event.preventDefault();
    await runWithButton(els.lookupSubmit, async () => {
        const shortString = extractShortString(els.lookupShortString.value);
        const data = await apiFetch(`/short-url/origin/${encodeURIComponent(shortString)}`);
        els.lookupResult.classList.remove("is-empty");
        els.lookupResult.innerHTML = renderUrlDetails(data);
    });
}

async function handleLogin(event) {
    event.preventDefault();
    await runWithButton(els.loginSubmit, async () => {
        const data = await apiFetch("/auth/login", {
            method: "POST",
            body: {
                username: els.loginUsername.value.trim(),
                password: els.loginPassword.value,
            },
        });
        setSession(data);
        els.loginForm.reset();
        showNotice("positive", "登入成功", data.username);
        loadMyUrls();
    });
}

async function handleRegister(event) {
    event.preventDefault();
    await runWithButton(els.registerSubmit, async () => {
        const data = await apiFetch("/auth/register", {
            method: "POST",
            body: {
                username: els.registerUsername.value.trim(),
                password: els.registerPassword.value,
            },
        });
        setSession(data);
        els.registerForm.reset();
        showNotice("positive", "註冊成功", data.username);
        loadMyUrls();
    });
}

async function refreshAccessToken() {
    if (!state.refresh) {
        showNotice("negative", "無法更新 Token", "目前沒有 refresh token。");
        return;
    }

    await runWithButton(els.refreshButton, async () => {
        const data = await apiFetch("/user/refresh-token", {
            method: "POST",
            auth: true,
            body: { refresh: state.refresh },
        });
        state.access = data.access;
        saveState();
        showNotice("positive", "Token 已更新", "新的 access token 已儲存。");
    });
}

async function handleCustomUrl(event) {
    event.preventDefault();
    await runWithButton(els.customSubmit, async () => {
        const payload = buildCreatePayload(els.customOriginUrl.value, els.customExpireDate.value);
        payload.short_string = els.customShortString.value.trim();
        const data = await apiFetch("/short-url-with-auth/custom", {
            method: "POST",
            auth: true,
            body: payload,
        });
        els.customUrlForm.reset();
        showNotice("positive", "自訂短網址已建立", data.short_url);
        loadMyUrls();
    });
}

async function loadMyUrls() {
    if (!isAuthenticated()) {
        renderMyUrls([]);
        return;
    }
    await runWithButton(els.refreshMyUrls, async () => {
        const urls = await apiFetch("/short-url-with-auth/all-my", { auth: true });
        renderMyUrls(urls);
    });
}

function renderMyUrls(urls) {
    els.myUrlsBody.innerHTML = "";
    if (!urls.length) {
        els.myUrlsEmpty.textContent = isAuthenticated() ? "目前沒有短網址。" : "登入後可檢視自己的短網址。";
        els.myUrlsEmpty.classList.remove("has-hidden");
        return;
    }

    els.myUrlsEmpty.classList.add("has-hidden");
    els.myUrlsBody.innerHTML = urls.map((url) => {
        const shortUrl = publicShortUrl(url);
        return `
            <tr>
                <td><span class="meta-chip">${escapeHtml(url.short_string)}</span></td>
                <td class="url-cell"><a href="${escapeAttr(url.origin_url)}" target="_blank" rel="noreferrer">${escapeHtml(url.origin_url)}</a></td>
                <td>${formatDate(url.create_date)}</td>
                <td>${url.expire_date ? formatDate(url.expire_date) : "不限制"}</td>
                <td>${url.visit_count}</td>
                <td class="is-collapsed">
                    <div class="row-actions">
                        <button class="ts-button is-icon is-secondary" type="button" title="複製短網址" data-copy="${escapeAttr(shortUrl)}">
                            <span class="ts-icon is-copy-icon"></span>
                        </button>
                        <a class="ts-button is-icon is-secondary" title="開啟短網址" href="${escapeAttr(shortUrl)}" target="_blank" rel="noreferrer">
                            <span class="ts-icon is-arrow-up-right-from-square-icon"></span>
                        </a>
                        <button class="ts-button is-icon is-negative is-outlined" type="button" title="刪除" data-delete="${escapeAttr(url.short_string)}">
                            <span class="ts-icon is-trash-icon"></span>
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }).join("");
}

async function handleMyUrlAction(event) {
    const copyValue = event.target.closest("[data-copy]")?.dataset.copy;
    const deleteValue = event.target.closest("[data-delete]")?.dataset.delete;

    if (copyValue) {
        await copyText(copyValue);
        showNotice("positive", "已複製", copyValue);
    }

    if (deleteValue) {
        if (!window.confirm(`刪除短碼 ${deleteValue}？`)) {
            return;
        }
        await apiFetch(`/short-url-with-auth/url/${encodeURIComponent(deleteValue)}`, {
            method: "DELETE",
            auth: true,
        });
        showNotice("positive", "已刪除", deleteValue);
        loadMyUrls();
    }
}

async function loadAdminUrls() {
    await runWithButton(els.adminLoadUrls, async () => {
        const urls = await apiFetch("/admin/all-urls", { auth: true });
        els.adminOutput.classList.remove("empty-state");
        els.adminOutput.innerHTML = `
            <div class="table-scroll">
                <table class="ts-table is-celled is-striped">
                    <thead>
                        <tr>
                            <th>短碼</th>
                            <th>原始網址</th>
                            <th>建立者</th>
                            <th>拜訪</th>
                            <th>到期</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${urls.map((url) => `
                            <tr>
                                <td><span class="meta-chip">${escapeHtml(url.short_string)}</span></td>
                                <td class="url-cell">${escapeHtml(url.origin_url)}</td>
                                <td>${escapeHtml(url.creator_username || "anonymous")}</td>
                                <td>${url.visit_count}</td>
                                <td>${url.expire_date ? formatDate(url.expire_date) : "不限制"}</td>
                            </tr>
                        `).join("")}
                    </tbody>
                </table>
            </div>
        `;
    });
}

async function loadAdminUsers() {
    await runWithButton(els.adminLoadUsers, async () => {
        const users = await apiFetch("/admin/users", { auth: true });
        els.adminOutput.classList.remove("empty-state");
        els.adminOutput.innerHTML = `
            <div class="table-scroll">
                <table class="ts-table is-celled is-striped">
                    <thead>
                        <tr>
                            <th>使用者</th>
                            <th>角色</th>
                            <th class="is-collapsed">操作</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${users.map((user) => `
                            <tr>
                                <td>${escapeHtml(user.username)}</td>
                                <td>
                                    <select class="ts-select user-type-select" data-user-type="${escapeAttr(user.username)}">
                                        <option value="0"${user.user_type === 0 ? " selected" : ""}>匿名</option>
                                        <option value="1"${user.user_type === 1 ? " selected" : ""}>一般</option>
                                        <option value="2"${user.user_type === 2 ? " selected" : ""}>管理員</option>
                                    </select>
                                </td>
                                <td class="is-collapsed">
                                    <div class="row-actions">
                                        <button class="ts-button is-secondary is-dense" type="button" data-update-user="${escapeAttr(user.username)}">更新</button>
                                        <button class="ts-button is-negative is-outlined is-dense" type="button" data-delete-user="${escapeAttr(user.username)}">刪除</button>
                                    </div>
                                </td>
                            </tr>
                        `).join("")}
                    </tbody>
                </table>
            </div>
        `;
    });
}

async function deleteExpiredUrls() {
    await runWithButton(els.adminExpireUrls, async () => {
        await apiFetch("/admin/expire-urls", {
            method: "DELETE",
            auth: true,
        });
        showNotice("positive", "已清除過期短網址", "管理員操作完成。");
    });
}

async function handleAdminAction(event) {
    const updateUser = event.target.closest("[data-update-user]")?.dataset.updateUser;
    const deleteUser = event.target.closest("[data-delete-user]")?.dataset.deleteUser;

    if (updateUser) {
        const select = els.adminOutput.querySelector(`[data-user-type="${cssEscape(updateUser)}"]`);
        await apiFetch(`/admin/user/${encodeURIComponent(updateUser)}`, {
            method: "PUT",
            auth: true,
            query: { user_type: select.value },
        });
        showNotice("positive", "使用者已更新", updateUser);
        loadAdminUsers();
    }

    if (deleteUser) {
        if (!window.confirm(`刪除使用者 ${deleteUser}？`)) {
            return;
        }
        await apiFetch(`/admin/user/${encodeURIComponent(deleteUser)}`, {
            method: "DELETE",
            auth: true,
        });
        showNotice("positive", "使用者已刪除", deleteUser);
        loadAdminUsers();
    }
}

function buildCreatePayload(originUrl, expireDate) {
    const payload = { origin_url: originUrl.trim() };
    const expire = toApiDateTime(expireDate);
    if (expire) {
        payload.expire_date = expire;
    }
    return payload;
}

function toApiDateTime(value) {
    if (!value) {
        return null;
    }
    return new Date(value).toISOString();
}

function extractShortString(value) {
    const raw = value.trim();
    try {
        const url = new URL(raw);
        const parts = url.pathname.split("/").filter(Boolean);
        return parts[parts.length - 1] || raw;
    } catch {
        return raw.replace(/^\/+|\/+$/g, "");
    }
}

function setSession(data) {
    state.user = {
        username: data.username,
        user_type: data.user_type,
    };
    state.access = data.access;
    state.refresh = data.refresh;
    saveState();
    renderSession();
}

function logout() {
    state.user = null;
    state.access = null;
    state.refresh = null;
    saveState();
    renderSession();
    renderMyUrls([]);
    showNotice("positive", "已登出", "本機 token 已清除。");
}

function renderSession() {
    els.sessionUser.textContent = isAuthenticated()
        ? `${state.user.username} / ${roleName(state.user.user_type)}`
        : "未登入";

    els.logoutButton.disabled = !isAuthenticated();
    els.refreshButton.disabled = !isAuthenticated();

    document.querySelectorAll("[data-auth-panel]").forEach((panel) => {
        panel.classList.toggle("is-disabled-panel", !isAuthenticated());
        panel.querySelectorAll("input, button, select").forEach((control) => {
            control.disabled = !isAuthenticated();
        });
    });

    els.adminPanel.classList.toggle("has-hidden", !isAdmin());
}

function roleName(userType) {
    if (userType === 2) {
        return "管理員";
    }
    if (userType === 0) {
        return "匿名";
    }
    return "一般使用者";
}

function renderUrlDetails(url) {
    const shortUrl = publicShortUrl(url);
    return `
        <dl>
            <dt>短網址</dt>
            <dd>
                <div class="copy-line">
                    <a href="${escapeAttr(shortUrl)}" target="_blank" rel="noreferrer">${escapeHtml(shortUrl)}</a>
                    <button class="ts-button is-icon is-secondary" type="button" title="複製" data-copy="${escapeAttr(shortUrl)}">
                        <span class="ts-icon is-copy-icon"></span>
                    </button>
                </div>
            </dd>
            <dt>短碼</dt>
            <dd>${escapeHtml(url.short_string)}</dd>
            <dt>原始網址</dt>
            <dd><a href="${escapeAttr(url.origin_url)}" target="_blank" rel="noreferrer">${escapeHtml(url.origin_url)}</a></dd>
            <dt>建立者</dt>
            <dd>${escapeHtml(url.creator_username || "anonymous")}</dd>
            <dt>建立時間</dt>
            <dd>${formatDate(url.create_date)}</dd>
            <dt>到期</dt>
            <dd>${url.expire_date ? formatDate(url.expire_date) : "不限制"}</dd>
            <dt>拜訪</dt>
            <dd>${url.visit_count}</dd>
        </dl>
    `;
}

function publicShortUrl(url) {
    try {
        return new URL(`/${url.short_string}`, new URL(state.apiBase).origin).toString();
    } catch {
        return url.short_url;
    }
}

document.addEventListener("click", async (event) => {
    const copyValue = event.target.closest("[data-copy]")?.dataset.copy;
    if (!copyValue) {
        return;
    }
    await copyText(copyValue);
    showNotice("positive", "已複製", copyValue);
});

async function copyText(text) {
    if (navigator.clipboard) {
        await navigator.clipboard.writeText(text);
        return;
    }
    const input = document.createElement("input");
    input.value = text;
    document.body.appendChild(input);
    input.select();
    document.execCommand("copy");
    input.remove();
}

async function runWithButton(button, task) {
    setLoading(button, true);
    try {
        await task();
    } catch (error) {
        showNotice("negative", "操作失敗", error.message);
    } finally {
        setLoading(button, false);
        renderSession();
    }
}

function setLoading(button, loading) {
    if (!button) {
        return;
    }
    button.disabled = loading;
    button.classList.toggle("is-loading", loading);
}

function showNotice(type, title, content) {
    els.notice.classList.remove("has-hidden", "is-negative", "is-positive", "is-warning");
    els.notice.classList.add(`is-${type}`);
    els.noticeTitle.textContent = title;
    els.noticeContent.textContent = content;
}

function hideNotice() {
    els.notice.classList.add("has-hidden");
}

function formatDate(value) {
    return new Intl.DateTimeFormat("zh-TW", {
        dateStyle: "medium",
        timeStyle: "short",
    }).format(new Date(value));
}

function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function escapeAttr(value) {
    return escapeHtml(value);
}

function cssEscape(value) {
    if (window.CSS?.escape) {
        return window.CSS.escape(value);
    }
    return String(value).replaceAll('"', '\\"');
}

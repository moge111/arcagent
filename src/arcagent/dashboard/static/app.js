// Terry Dashboard

const API = '/api';

async function fetchJSON(path) {
    try {
        const res = await fetch(API + path);
        return res.json();
    } catch (e) {
        console.error('Fetch failed:', path, e);
        return null;
    }
}

function formatUptime(seconds) {
    const d = Math.floor(seconds / 86400);
    const h = Math.floor((seconds % 86400) / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    if (d > 0) return `${d}d ${h}h`;
    if (h > 0) return `${h}h ${m}m`;
    return `${m}m`;
}

function timeAgo(timestamp) {
    const seconds = Math.floor(Date.now() / 1000 - timestamp);
    if (seconds < 60) return 'just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    return `${Math.floor(seconds / 86400)}d ago`;
}

// --- Status ---
async function refreshStatus() {
    const data = await fetchJSON('/status');
    const badge = document.getElementById('status-badge');

    if (!data) {
        badge.textContent = 'Offline';
        badge.className = 'badge offline';
        return;
    }

    document.getElementById('uptime').textContent = formatUptime(data.uptime_seconds);
    document.getElementById('sessions').textContent = data.active_sessions;
    document.getElementById('skills-count').textContent = `${data.skills_enabled}/${data.skills_loaded}`;
    document.getElementById('tools-count').textContent = data.tools_available;

    badge.textContent = 'Online';
    badge.className = 'badge running';
}

// --- Skills ---
async function refreshSkills() {
    const data = await fetchJSON('/skills');
    const container = document.getElementById('skills-list');
    const badge = document.getElementById('skills-enabled-badge');

    if (!data || !data.skills || data.skills.length === 0) {
        container.innerHTML = '<p class="muted">No skills loaded</p>';
        badge.textContent = '0 enabled';
        return;
    }

    const enabled = data.skills.filter(s => s.enabled).length;
    badge.textContent = `${enabled} enabled`;

    container.innerHTML = data.skills.map(skill => `
        <div class="skill-item">
            <div class="skill-info">
                <div class="skill-name">${skill.name}</div>
                <div class="skill-desc">${skill.description || 'No description'}</div>
            </div>
            <label class="toggle">
                <input type="checkbox" ${skill.enabled ? 'checked' : ''}
                       onchange="toggleSkill('${skill.name}')">
                <span class="slider"></span>
            </label>
        </div>
    `).join('');
}

async function toggleSkill(name) {
    await fetch(`${API}/skills/${name}/toggle`, { method: 'POST' });
    await refreshSkills();
    await refreshStatus();
}

// --- Tools ---
async function refreshTools() {
    const data = await fetchJSON('/tools');
    const container = document.getElementById('tools-list');
    const badge = document.getElementById('tools-badge');

    if (!data || !data.tools || data.tools.length === 0) {
        container.innerHTML = '<p class="muted">No tools registered</p>';
        badge.textContent = '0 registered';
        return;
    }

    badge.textContent = `${data.tools.length} registered`;

    container.innerHTML = data.tools.map(tool => `
        <div class="tool-item">
            <div class="tool-info">
                <div class="tool-name">${tool.name}</div>
                <div class="tool-desc">${tool.description || ''}</div>
            </div>
        </div>
    `).join('');
}

// --- Conversations ---
async function refreshConversations() {
    const data = await fetchJSON('/conversations');
    const container = document.getElementById('convos-list');
    const badge = document.getElementById('convos-badge');

    if (!data || !data.conversations || data.conversations.length === 0) {
        container.innerHTML = '<p class="muted">No active conversations</p>';
        badge.textContent = '0';
        return;
    }

    badge.textContent = data.conversations.length.toString();

    container.innerHTML = data.conversations.map(c => `
        <div class="convo-item">
            <span class="convo-id">#${c.id.slice(-6)}</span>
            <span class="convo-meta">${c.message_count} msgs &middot; ${timeAgo(c.last_active)}</span>
        </div>
    `).join('');
}

// --- Logs ---
async function refreshLogs() {
    const data = await fetchJSON('/logs?limit=50');
    const container = document.getElementById('logs-list');

    if (!data || !data.logs || data.logs.length === 0) {
        container.innerHTML = '<p class="muted">No activity yet</p>';
        return;
    }

    container.innerHTML = data.logs.reverse().map(log => {
        const time = new Date(log.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        return `<div class="log-entry">
            <span class="time">${time}</span>
            <span class="level level-${log.level}">${log.level}</span>
            <span class="msg">${log.message}</span>
        </div>`;
    }).join('');

    container.scrollTop = 0;
}

// --- Init ---
async function init() {
    await Promise.all([
        refreshStatus(),
        refreshSkills(),
        refreshTools(),
        refreshConversations(),
        refreshLogs(),
    ]);
}

init();

// Auto-refresh
setInterval(refreshStatus, 5000);
setInterval(refreshConversations, 10000);
setInterval(refreshLogs, 15000);

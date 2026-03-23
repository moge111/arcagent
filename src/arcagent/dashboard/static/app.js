// ArcAgent Dashboard - Vanilla JS

const API = '/api';

async function fetchJSON(path) {
    const res = await fetch(API + path);
    return res.json();
}

function formatUptime(seconds) {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = seconds % 60;
    if (h > 0) return `${h}h ${m}m`;
    if (m > 0) return `${m}m ${s}s`;
    return `${s}s`;
}

async function refreshStatus() {
    try {
        const data = await fetchJSON('/status');
        document.getElementById('uptime').textContent = formatUptime(data.uptime_seconds);
        document.getElementById('sessions').textContent = data.active_sessions;
        document.getElementById('skills-count').textContent = `${data.skills_enabled}/${data.skills_loaded}`;
        document.getElementById('tools-count').textContent = data.tools_available;

        const badge = document.getElementById('status-badge');
        badge.textContent = data.status;
        badge.className = 'badge ' + data.status;
    } catch (e) {
        const badge = document.getElementById('status-badge');
        badge.textContent = 'offline';
        badge.className = 'badge error';
    }
}

async function refreshSkills() {
    try {
        const data = await fetchJSON('/skills');
        const container = document.getElementById('skills-list');

        if (!data.skills || data.skills.length === 0) {
            container.innerHTML = '<p class="muted">No skills loaded.</p>';
            return;
        }

        container.innerHTML = data.skills.map(skill => `
            <div class="skill-item">
                <div>
                    <span class="skill-name">${skill.name}</span>
                    <div class="skill-desc">${skill.description || 'No description'}</div>
                </div>
                <label class="toggle">
                    <input type="checkbox" ${skill.enabled ? 'checked' : ''}
                           onchange="toggleSkill('${skill.name}')">
                    <span class="slider"></span>
                </label>
            </div>
        `).join('');
    } catch (e) {
        console.error('Failed to load skills:', e);
    }
}

async function toggleSkill(name) {
    try {
        await fetch(`${API}/skills/${name}/toggle`, { method: 'POST' });
        await refreshSkills();
        await refreshStatus();
    } catch (e) {
        console.error('Failed to toggle skill:', e);
    }
}

async function refreshLogs() {
    try {
        const data = await fetchJSON('/logs?limit=30');
        const container = document.getElementById('logs-list');

        if (!data.logs || data.logs.length === 0) {
            container.innerHTML = '<p class="muted">No logs yet.</p>';
            return;
        }

        container.innerHTML = data.logs.reverse().map(log => {
            const time = new Date(log.timestamp).toLocaleTimeString();
            return `<div class="log-entry">
                <span class="time">${time}</span>
                <span class="level-${log.level}">[${log.level}]</span>
                <span>${log.message}</span>
            </div>`;
        }).join('');
    } catch (e) {
        console.error('Failed to load logs:', e);
    }
}

// Initial load
refreshStatus();
refreshSkills();
refreshLogs();

// Auto-refresh
setInterval(refreshStatus, 5000);
setInterval(refreshLogs, 10000);

/**
 * Home Page Logic
 */

document.addEventListener('DOMContentLoaded', () => {
    loadHomeData();
});

async function loadHomeData() {
    try {
        const stats = await API.getStats();
        
        // Update hero stats with real numbers from the DB
        const statsContainer = document.getElementById('hero-stats');
        statsContainer.innerHTML = `
            <div class="hero-stat animate-in">
                <div class="stat-number">${formatNumber(stats.total_donors)}<span class="accent">+</span></div>
                <div class="stat-label">Registered Donors</div>
            </div>
            <div class="hero-stat animate-in">
                <div class="stat-number">${formatNumber(stats.lives_saved)}<span class="accent">+</span></div>
                <div class="stat-label">Lives Saved</div>
            </div>
            <div class="hero-stat animate-in hide-mobile">
                <div class="stat-number">${formatNumber(stats.fulfilled_requests)}<span class="accent"></span></div>
                <div class="stat-label">Requests Fulfilled</div>
            </div>
        `;

        // Update urgent requests
        const reqContainer = document.getElementById('urgent-cards-container');
        if (stats.recent_requests && stats.recent_requests.length > 0) {
            reqContainer.innerHTML = stats.recent_requests.slice(0, 3).map(req => `
                <div class="urgent-card">
                    <div class="blood-badge">${req.blood_group_needed}</div>
                    <div class="urgent-info" style="flex:1;">
                        <h4>${req.hospital_name}</h4>
                        <p>${req.city} • ${timeAgo(req.created_at)}</p>
                    </div>
                    <span class="urgency-tag ${req.urgency}">${req.urgency}</span>
                </div>
            `).join('');
        } else {
            reqContainer.innerHTML = `<div style="grid-column:1/-1;color:var(--text-muted);padding:20px 0;">No urgent requests at the moment.</div>`;
        }

    } catch (error) {
        console.error('Failed to load home data:', error);
        // Show fallback — don't leave dashes forever
        const statsContainer = document.getElementById('hero-stats');
        statsContainer.innerHTML = `
            <div class="hero-stat animate-in">
                <div class="stat-number">—</div>
                <div class="stat-label">Registered Donors</div>
            </div>
            <div class="hero-stat animate-in">
                <div class="stat-number">—</div>
                <div class="stat-label">Lives Saved</div>
            </div>
        `;
    }
}

function formatNumber(num) {
    if (!num && num !== 0) return '—';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'k';
    return num;
}

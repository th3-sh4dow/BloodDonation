/**
 * Auth Module — Login, Register, Session Management
 */

let currentUser = null;
let isAuthenticated = false;
let isStaff = false;

/**
 * Check authentication status on page load
 */
async function checkAuthStatus() {
    try {
        const data = await API.checkAuth();
        isAuthenticated = data.authenticated;
        if (isAuthenticated) {
            currentUser = data.user;
            isStaff = data.is_staff || false;
            // Store in sessionStorage for quick access
            sessionStorage.setItem('user', JSON.stringify(data.user));
            sessionStorage.setItem('profile', JSON.stringify(data.profile));
            sessionStorage.setItem('isStaff', data.is_staff);
        } else {
            currentUser = null;
            sessionStorage.removeItem('user');
            sessionStorage.removeItem('profile');
            sessionStorage.removeItem('isStaff');
        }
        updateAuthUI();
    } catch (error) {
        console.error('Auth check failed:', error);
        isAuthenticated = false;
        currentUser = null;
        updateAuthUI();
    }
}

/**
 * Update navigation UI based on auth state
 */
function updateAuthUI() {
    const authSection = document.querySelector('.nav-auth');
    if (!authSection) return;

    if (isAuthenticated && currentUser) {
        const profile = JSON.parse(sessionStorage.getItem('profile') || '{}');
        const initials = (currentUser.first_name?.[0] || '') + (currentUser.last_name?.[0] || '');
        authSection.innerHTML = `
            <button class="nav-notification-btn" onclick="window.location.href='dashboard.html'" title="Notifications">
                🔔
                <span class="nav-notification-badge" id="notif-badge" style="display:none">0</span>
            </button>
            <a href="dashboard.html" class="btn btn-sm btn-secondary" style="gap: 8px;">
                <span style="width:28px;height:28px;background:var(--gradient-crimson);border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-size:0.75rem;font-weight:700;color:#fff;">${initials || '?'}</span>
                ${currentUser.first_name || currentUser.username}
            </a>
            ${isStaff ? '<a href="admin-panel.html" class="btn btn-sm btn-outline">Admin</a>' : ''}
            <button class="btn btn-sm btn-secondary" onclick="handleLogout()">Logout</button>
        `;
        // Check notifications
        loadNotificationCount();
    } else {
        authSection.innerHTML = `
            <a href="login.html" class="btn btn-sm btn-secondary">Sign In</a>
            <a href="register.html" class="btn btn-sm btn-primary">Register</a>
        `;
    }
}

/**
 * Load notification count
 */
async function loadNotificationCount() {
    try {
        const data = await API.getNotifications();
        const badge = document.getElementById('notif-badge');
        if (badge && data.unread_count > 0) {
            badge.textContent = data.unread_count;
            badge.style.display = 'flex';
        }
    } catch (e) { /* silent */ }
}

/**
 * Handle logout
 */
async function handleLogout() {
    try {
        await API.logout();
        isAuthenticated = false;
        currentUser = null;
        sessionStorage.clear();
        showToast('Logged out successfully!', 'success');
        setTimeout(() => window.location.href = 'index.html', 500);
    } catch (error) {
        showToast('Logout failed', 'error');
    }
}

/**
 * Require authentication — redirect to login if not authenticated
 */
function requireAuth() {
    if (!isAuthenticated) {
        window.location.href = 'login.html';
        return false;
    }
    return true;
}

/**
 * Require admin — redirect if not staff
 */
function requireAdmin() {
    if (!isStaff) {
        window.location.href = 'index.html';
        return false;
    }
    return true;
}

// Initialize auth on DOMContentLoaded
document.addEventListener('DOMContentLoaded', () => {
    checkAuthStatus();
    initNavbar();
});

/**
 * Initialize navbar scroll behavior & mobile toggle
 */
function initNavbar() {
    const navbar = document.querySelector('.navbar');
    const toggle = document.querySelector('.nav-toggle');
    const links = document.querySelector('.nav-links');

    // Scroll effect
    if (navbar) {
        let lastScroll = 0;
        window.addEventListener('scroll', () => {
            const currentScroll = window.scrollY;
            if (currentScroll > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
            lastScroll = currentScroll;
        });
    }

    // Mobile toggle
    if (toggle && links) {
        toggle.addEventListener('click', () => {
            links.classList.toggle('open');
        });

        // Close on link click
        links.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => links.classList.remove('open'));
        });
    }

    // Set active nav link
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    document.querySelectorAll('.nav-links a').forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPage) {
            link.classList.add('active');
        }
    });
}

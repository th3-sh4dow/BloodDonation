/**
 * API Client — Centralized fetch wrapper for Blood Donation API
 * Auto-detects local dev vs production (Render)
 */

// Set VITE_API_URL or REACT_APP_API_URL in env, OR
// hardcode your Render backend URL below after deploying:
//   const PRODUCTION_API = 'https://your-backend-name.onrender.com/api';
const PRODUCTION_API = window.__BLOODDROP_API__ || '';

const API_BASE = PRODUCTION_API || (
    window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
        ? 'http://127.0.0.1:8000/api'
        : `${window.location.protocol}//${window.location.hostname}/api`
);

/**
 * Get CSRF token from cookie (required for Django session auth)
 */
function getCSRFToken() {
    const name = 'csrftoken';
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith(name + '=')) {
            return cookie.substring(name.length + 1);
        }
    }
    return '';
}

/**
 * Make an API request
 */
async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const config = {
        credentials: 'include', // Send cookies for session auth
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
            ...options.headers,
        },
        ...options,
    };

    if (config.body && typeof config.body === 'object') {
        config.body = JSON.stringify(config.body);
    }

    try {
        const response = await fetch(url, config);
        const data = await response.json();

        if (!response.ok) {
            throw { status: response.status, data };
        }

        return data;
    } catch (error) {
        if (error.status) throw error;
        console.error('API Error:', error);
        throw { status: 0, data: { error: 'Network error. Is the server running?' } };
    }
}

/**
 * API Methods
 */
const API = {
    // Auth
    register: (data) => apiRequest('/register/', { method: 'POST', body: data }),
    login: (data) => apiRequest('/login/', { method: 'POST', body: data }),
    logout: () => apiRequest('/logout/', { method: 'POST' }),
    checkAuth: () => apiRequest('/auth/check/'),

    // Profile
    getProfile: () => apiRequest('/profile/'),
    updateProfile: (data) => apiRequest('/profile/', { method: 'PUT', body: data }),

    // Donors
    getDonors: (params = {}) => {
        const query = new URLSearchParams(params).toString();
        return apiRequest(`/donors/?${query}`);
    },

    // Blood Requests
    getRequests: (params = {}) => {
        const query = new URLSearchParams(params).toString();
        return apiRequest(`/requests/?${query}`);
    },
    createRequest: (data) => apiRequest('/requests/', { method: 'POST', body: data }),
    getRequest: (id) => apiRequest(`/requests/${id}/`),
    updateRequest: (id, data) => apiRequest(`/requests/${id}/`, { method: 'PUT', body: data }),

    // Donations
    getDonations: () => apiRequest('/donations/'),
    recordDonation: (data) => apiRequest('/donations/', { method: 'POST', body: data }),

    // Notifications
    getNotifications: () => apiRequest('/notifications/'),
    markRead: (id) => apiRequest(`/notifications/${id}/read/`, { method: 'PUT' }),
    markAllRead: () => apiRequest('/notifications/read-all/', { method: 'PUT' }),

    // Inventory
    getInventory: () => apiRequest('/inventory/'),

    // Stats
    getStats: () => apiRequest('/stats/'),

    // Contact
    sendContact: (data) => apiRequest('/contact/', { method: 'POST', body: data }),

    // Admin
    adminGetDonors: (params = {}) => {
        const query = new URLSearchParams(params).toString();
        return apiRequest(`/admin/donors/?${query}`);
    },
    adminGetRequests: (params = {}) => {
        const query = new URLSearchParams(params).toString();
        return apiRequest(`/admin/requests/?${query}`);
    },
    adminUpdateInventory: (bloodGroup, units) =>
        apiRequest(`/admin/inventory/${encodeURIComponent(bloodGroup)}/`, {
            method: 'PUT',
            body: { units_available: units },
        }),
};


/**
 * Toast Notification System
 */
function showToast(message, type = 'info', duration = 4000) {
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    const icons = { success: '✓', error: '✕', info: 'ℹ' };
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <span>${icons[type] || 'ℹ'}</span>
        <span>${message}</span>
        <button class="toast-close" onclick="this.parentElement.remove()">×</button>
    `;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideOutRight 0.3s ease forwards';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}


/**
 * Format date helper
 */
function formatDate(dateStr) {
    if (!dateStr) return '—';
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-IN', { year: 'numeric', month: 'short', day: 'numeric' });
}

function timeAgo(dateStr) {
    const now = new Date();
    const d = new Date(dateStr);
    const seconds = Math.floor((now - d) / 1000);
    if (seconds < 60) return 'Just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;
    return formatDate(dateStr);
}

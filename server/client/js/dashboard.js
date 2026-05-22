/**
 * Dashboard Logic
 */

let userProfile = null;

document.addEventListener('DOMContentLoaded', async () => {
    // Wait for auth to ensure currentUser is set
    setTimeout(() => {
        if (requireAuth()) {
            initDashboard();
        }
    }, 500);

    document.getElementById('recordDonationForm').addEventListener('submit', handleRecordDonation);
    
    // Set max date for donation to today
    const dateInput = document.getElementById('donateDate');
    if (dateInput) {
        const today = new Date().toISOString().split('T')[0];
        dateInput.max = today;
        dateInput.value = today;
    }
});

async function initDashboard() {
    loadProfile();
    loadDonations();
    loadMyRequests();
    loadNotifications();
}

async function loadProfile() {
    try {
        userProfile = await API.getProfile();
        sessionStorage.setItem('profile', JSON.stringify(userProfile)); // update session
        
        const card = document.getElementById('profileCard');
        card.innerHTML = `
            <div class="profile-avatar">${userProfile.blood_group}</div>
            <h2 style="font-size:1.4rem;margin-bottom:4px;">${currentUser.first_name} ${currentUser.last_name || ''}</h2>
            <p style="color:var(--text-secondary);font-size:0.95rem;">${userProfile.city}, ${userProfile.state}</p>
            
            <div class="eligibility-badge ${userProfile.is_eligible ? 'eligible' : 'not-eligible'}">
                ${userProfile.is_eligible ? '✨ Eligible to Donate' : `⏳ Eligible on ${formatDate(userProfile.next_eligible_date)}`}
            </div>
            
            <div style="display:flex;gap:12px;margin-top:24px;padding-top:20px;border-top:1px solid var(--border-color);">
                <div style="flex:1;">
                    <div style="font-size:1.5rem;font-weight:700;font-family:'Outfit',sans-serif;">${userProfile.total_donations}</div>
                    <div style="font-size:0.8rem;color:var(--text-secondary);">Donations</div>
                </div>
                <div style="width:1px;background:var(--border-color);"></div>
                <div style="flex:1;">
                    <div style="font-size:1.5rem;font-weight:700;font-family:'Outfit',sans-serif;color:var(--crimson-light);">${userProfile.total_donations * 3}</div>
                    <div style="font-size:0.8rem;color:var(--text-secondary);">Lives Saved</div>
                </div>
            </div>
        `;

        const btnToggleNode = document.getElementById('toggleAvailabilityBtn');
        if(btnToggleNode) {
            btnToggleNode.innerHTML = userProfile.is_available ? 'Make Unavailable' : 'Make Available';
            btnToggleNode.className = userProfile.is_available ? 'btn btn-outline' : 'btn btn-secondary';
        }
    } catch (e) {
        console.error('Profile load failed', e);
    }
}

async function toggleAvailability() {
    if (!userProfile) return;
    try {
        const newState = !userProfile.is_available;
        await API.updateProfile({ is_available: newState });
        showToast(newState ? 'You are now marked as available' : 'You are now marked as unavailable', 'success');
        loadProfile(); // refresh UI
    } catch (e) {
        showToast('Failed to update status', 'error');
    }
}

async function loadDonations() {
    try {
        const data = await API.getDonations();
        const timeline = document.getElementById('donationsTimeline');
        
        if (data.donations && data.donations.length > 0) {
            timeline.innerHTML = data.donations.map(d => `
                <div class="timeline-item animate-in">
                    <h4>Donated ${d.units} unit(s) at ${d.hospital_name}</h4>
                    <p>Blood Group: <strong>${d.blood_group}</strong></p>
                    <div class="timeline-date">${formatDate(d.donation_date)}</div>
                </div>
            `).join('');
        } else {
            timeline.innerHTML = `
                <div class="empty-state">
                    <h3>No donations recorded yet</h3>
                    <p>When you donate blood, record it here to track your impact!</p>
                </div>
            `;
        }
    } catch (e) {
        console.error('Donations load failed', e);
    }
}

async function loadMyRequests() {
    try {
        // Fetch only requests made by logged in user.
        // Quick hack for UI: fetch all open/fulfilled and filter by user ID manually since we didn't explicitly separate endpoint.
        const data = await API.getRequests(); // backend actually returns all; let's filter purely client side for simplicity.
        
        const myReqs = data.requests.filter(req => req.requester === currentUser.id);
        const listContainer = document.getElementById('myRequestsList');
        
        if (myReqs.length > 0) {
            listContainer.innerHTML = myReqs.map(req => `
                <div class="card card-glass animate-in" style="margin-bottom:16px;padding:20px;">
                    <div style="display:flex;justify-content:space-between;margin-bottom:12px;">
                        <h4 style="font-size:1.1rem;">${req.patient_name} - ${req.hospital_name}</h4>
                        <span class="status-badge ${req.status}">${req.status}</span>
                    </div>
                    <div style="display:flex;gap:16px;font-size:0.9rem;color:var(--text-secondary);flex-wrap:wrap;">
                        <span style="background:var(--bg-tertiary);padding:4px 10px;border-radius:12px;">🩸 ${req.blood_group_needed}</span>
                        <span style="background:var(--bg-tertiary);padding:4px 10px;border-radius:12px;">💧 ${req.units_needed} Unit(s)</span>
                        <span style="background:var(--bg-tertiary);padding:4px 10px;border-radius:12px;">📅 ${formatDate(req.created_at)}</span>
                    </div>
                    ${req.status === 'open' ? `
                        <div style="margin-top:16px;padding-top:16px;border-top:1px solid var(--border-color);">
                            <button class="btn btn-sm btn-outline" onclick="updateRequestStatus(${req.id}, 'fulfilled')">Mark Fulfilled</button>
                            <button class="btn btn-sm btn-secondary" onclick="updateRequestStatus(${req.id}, 'cancelled')">Cancel Request</button>
                        </div>
                    ` : ''}
                </div>
            `).join('');
        } else {
            listContainer.innerHTML = `<div class="empty-state">You haven't made any requests yet.</div>`;
        }
    } catch (e) {
        console.error('My requests load failed', e);
    }
}

async function updateRequestStatus(id, newStatus) {
    try {
        await API.updateRequest(id, { status: newStatus });
        showToast('Request updated', 'success');
        loadMyRequests();
    } catch (e) {
        showToast('Failed to update request', 'error');
    }
}

async function loadNotifications() {
    try {
        const data = await API.getNotifications();
        const list = document.getElementById('notificationsList');
        const badge = document.getElementById('tabNotifCount');
        
        if (data.unread_count > 0) {
            badge.style.display = 'inline-block';
            badge.innerText = data.unread_count;
        } else {
            badge.style.display = 'none';
        }

        if (data.notifications && data.notifications.length > 0) {
            list.innerHTML = data.notifications.map(n => `
                <div class="notification-item ${!n.is_read ? 'unread' : ''}" onclick="markNotificationRead(${n.id})">
                    <div class="notification-icon ${n.notification_type}">
                        ${n.notification_type === 'emergency' ? '🚨' : n.notification_type === 'success' ? '✅' : '🔔'}
                    </div>
                    <div class="notification-content">
                        <h4>${n.title}</h4>
                        <p>${n.message}</p>
                        <div class="notification-time">${timeAgo(n.created_at)}</div>
                    </div>
                </div>
            `).join('');
        } else {
            list.innerHTML = `<div style="padding:40px;text-align:center;color:var(--text-muted);">No new notifications</div>`;
        }
    } catch (e) {
        console.error('Notifications load failed', e);
    }
}

async function markNotificationRead(id) {
    try {
        await API.markRead(id);
        loadNotifications();
        // Also update navbar badge from auth.js if exists
        if(typeof loadNotificationCount === 'function') loadNotificationCount();
    } catch (e) {}
}

async function markAllNotificationsRead() {
    try {
        await API.markAllRead();
        loadNotifications();
        showToast('All notifications marked as read', 'info');
        if(typeof loadNotificationCount === 'function') loadNotificationCount();
    } catch (e) {}
}

async function handleRecordDonation(e) {
    e.preventDefault();
    const data = {
        donation_date: document.getElementById('donateDate').value,
        units: document.getElementById('donateUnits').value,
        hospital_name: document.getElementById('donateHospital').value,
        blood_group: userProfile.blood_group // automatically use the user's blood group
    };

    try {
        await API.recordDonation(data);
        showToast('Donation recorded successfully! 🎉', 'success');
        closeModal('donateModal');
        e.target.reset();
        
        // Refresh modules
        loadProfile();
        loadDonations();
    } catch (err) {
        showToast('Failed to record donation', 'error');
    }
}

/* UI Helpers */
function switchTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
    
    document.getElementById(`tab-${tabId}`).classList.add('active');
    event.currentTarget.classList.add('active');
}

function showDonateModal() {
    document.getElementById('donateModal').classList.add('active');
}

function closeModal(id) {
    document.getElementById(id).classList.remove('active');
}

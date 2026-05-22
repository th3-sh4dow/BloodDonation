/**
 * Admin Panel Logic
 */

document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        if (requireAuth() && requireAdmin()) {
            initAdmin();
        }
    }, 500);

    // Search input listener
    let searchTimeout;
    document.getElementById('donorSearch')?.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            loadDonors(e.target.value);
        }, 400);
    });
});

function initAdmin() {
    loadInventory();
    loadRequests();
    loadDonors();
}

/* Navigation */
function switchAdminTab(tabId) {
    document.querySelectorAll('.admin-tab').forEach(el => el.style.display = 'none');
    document.querySelectorAll('.tab-menu-btn').forEach(el => el.classList.remove('active'));
    
    document.getElementById(`admin-${tabId}`).style.display = 'block';
    event.currentTarget.classList.add('active');
}

/* Inventory Management */
async function loadInventory() {
    try {
        const data = await API.getInventory();
        const grid = document.getElementById('inventoryGrid');
        
        // Define all groups to ensure they all show up even if 0
        const allGroups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'];
        const inventoryMap = {};
        
        if (data.inventory) {
            data.inventory.forEach(item => inventoryMap[item.blood_group] = item.units_available);
        }

        grid.innerHTML = allGroups.map(group => {
            const units = inventoryMap[group] || 0;
            // Calculate height percentage (max visual cap at 100 units for bar height)
            let heightPct = (units / 100) * 100;
            if (heightPct > 100) heightPct = 100;
            if (heightPct < 5 && units > 0) heightPct = 5; // minimum visible height if has units
            
            return `
                <div class="inventory-item animate-in" style="cursor:pointer;" onclick="openEditInventory('${group}', ${units})">
                    <div class="inventory-bar-container">
                        <div class="inventory-bar-fill" style="height: ${heightPct}%"></div>
                    </div>
                    <div class="inv-group">${group}</div>
                    <div class="inv-units">${units} units</div>
                    <div style="font-size:0.7rem;color:var(--crimson-light);margin-top:6px;">Edit ✏️</div>
                </div>
            `;
        }).join('');
    } catch (e) {
        showToast('Failed to load inventory', 'error');
    }
}

function openEditInventory(group, currentUnits) {
    document.getElementById('editInvGroup').textContent = group;
    document.getElementById('editInvUnits').value = currentUnits;
    document.getElementById('editInvModal').classList.add('active');
}

async function saveInventory() {
    const group = document.getElementById('editInvGroup').textContent;
    const units = document.getElementById('editInvUnits').value;
    
    try {
        await API.adminUpdateInventory(group, units);
        showToast('Inventory updated', 'success');
        closeModal('editInvModal');
        loadInventory(); // refresh
    } catch (e) {
        showToast('Update failed', 'error');
    }
}

/* Blood Requests Management */
async function loadRequests() {
    try {
        const data = await API.adminGetRequests();
        const tbody = document.getElementById('requestsTableBody');
        
        if (data.requests && data.requests.length > 0) {
            tbody.innerHTML = data.requests.map(req => `
                <tr>
                    <td>
                        <div style="font-weight:600;color:var(--text-primary);">${req.patient_name}</div>
                        <div style="font-size:0.8rem;color:var(--text-muted);">${req.hospital_name}</div>
                    </td>
                    <td><span class="blood-group-badge sm" style="width:32px;height:32px;">${req.blood_group_needed}</span></td>
                    <td>${req.units_needed}</td>
                    <td><span class="urgency-tag ${req.urgency}">${req.urgency}</span></td>
                    <td>${req.city}</td>
                    <td><span class="status-badge ${req.status}">${req.status}</span></td>
                    <td>
                        <select class="form-select" style="padding:4px 8px;font-size:0.8rem;width:auto;" onchange="updateAdminReqStatus(${req.id}, this.value)">
                            <option value="open" ${req.status === 'open' ? 'selected' : ''}>Open</option>
                            <option value="fulfilled" ${req.status === 'fulfilled' ? 'selected' : ''}>Fulfilled</option>
                            <option value="expired" ${req.status === 'expired' ? 'selected' : ''}>Expired</option>
                            <option value="cancelled" ${req.status === 'cancelled' ? 'selected' : ''}>Cancelled</option>
                        </select>
                    </td>
                </tr>
            `).join('');
        } else {
            tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:30px;">No requests found.</td></tr>`;
        }
    } catch (e) {
        showToast('Failed to load requests', 'error');
    }
}

async function updateAdminReqStatus(id, status) {
    try {
        await API.updateRequest(id, { status: status });
        showToast('Status updated', 'success');
        loadRequests();
    } catch (e) {
        showToast('Failed to update status', 'error');
    }
}

/* Donor Management */
async function loadDonors(searchQuery = '') {
    try {
        const data = await API.adminGetDonors(searchQuery ? { search: searchQuery } : {});
        const tbody = document.getElementById('donorsTableBody');
        
        if (data.donors && data.donors.length > 0) {
            tbody.innerHTML = data.donors.map(donor => `
                <tr>
                    <td style="font-weight:600;color:var(--text-primary);">${donor.user.first_name} ${donor.user.last_name || ''}</td>
                    <td>${donor.user.email}</td>
                    <td><span style="font-family:'Outfit',sans-serif;font-weight:700;color:var(--crimson-light);">${donor.blood_group}</span></td>
                    <td>${donor.city}, ${donor.state}</td>
                    <td>${donor.is_available ? '<span class="status-badge fulfilled">Available</span>' : '<span class="status-badge cancelled">Unavailable</span>'}</td>
                    <td>${donor.total_donations}</td>
                </tr>
            `).join('');
        } else {
            tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;padding:30px;">No donors found matching criteria.</td></tr>`;
        }
    } catch (e) {
        showToast('Failed to load donors', 'error');
    }
}

function closeModal(id) {
    document.getElementById(id).classList.remove('active');
}

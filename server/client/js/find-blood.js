/**
 * Find Blood Donors Logic
 */

document.addEventListener('DOMContentLoaded', () => {
    // Populate select if URL params exist
    const urlParams = new URLSearchParams(window.location.search);
    if(urlParams.get('group')) document.getElementById('bloodGroup').value = urlParams.get('group');
    if(urlParams.get('city')) document.getElementById('city').value = urlParams.get('city');

    loadDonors();

    document.getElementById('searchForm').addEventListener('submit', (e) => {
        e.preventDefault();
        loadDonors();
    });
});

async function loadDonors() {
    const bloodGroup = document.getElementById('bloodGroup').value;
    const city = document.getElementById('city').value;
    const grid = document.getElementById('donorsGrid');
    const emptyState = document.getElementById('emptyState');
    const resultsInfo = document.getElementById('resultsInfo');

    grid.innerHTML = `
        <div class="skeleton" style="height:140px;border-radius:var(--radius-lg);"></div>
        <div class="skeleton" style="height:140px;border-radius:var(--radius-lg);"></div>
        <div class="skeleton" style="height:140px;border-radius:var(--radius-lg);"></div>
    `;
    emptyState.style.display = 'none';

    try {
        const data = await API.getDonors({ blood_group: bloodGroup, city: city });
        
        let headerText = `Found ${data.total} eligible donor(s)`;
        if (bloodGroup && data.compatible_groups) {
            headerText += ` (including compatible groups: ${data.compatible_groups.join(', ')})`;
        }
        resultsInfo.textContent = headerText;

        if (data.donors && data.donors.length > 0) {
            grid.innerHTML = data.donors.map((donor, index) => renderDonorCard(donor, index)).join('');
        } else {
            grid.innerHTML = '';
            emptyState.style.display = 'block';
        }
    } catch (error) {
        grid.innerHTML = '';
        showToast('Failed to load donors', 'error');
    }
}

function renderDonorCard(donor, index) {
    const isExactMatch = !document.getElementById('bloodGroup').value || donor.blood_group === document.getElementById('bloodGroup').value;
    
    return `
        <div class="donor-card animate-in" style="animation-delay: ${index * 0.05}s">
            <div class="blood-group-badge sm" ${!isExactMatch ? 'style="background:var(--bg-tertiary);color:var(--text-primary);box-shadow:none"' : ''}>
                ${donor.blood_group}
            </div>
            <div class="donor-info">
                <h4>${donor.user.first_name} ${donor.user.last_name || ''}</h4>
                <div class="donor-meta">
                    <span>📍 ${donor.city}</span>
                    <span>🩸 ${donor.total_donations} Donations</span>
                </div>
                <div class="donor-tags">
                    ${donor.is_available ? '<span class="tag tag-available">Available</span>' : '<span class="tag tag-not-eligible">Not Available</span>'}
                    ${donor.is_eligible ? '<span class="tag tag-eligible">Eligible</span>' : '<span class="tag tag-not-eligible">Ineligible</span>'}
                </div>
            </div>
            <button class="btn btn-outline btn-sm" onclick='showContact(${JSON.stringify(donor).replace(/'/g, "&apos;")})'>Contact</button>
        </div>
    `;
}

function showContact(donor) {
    if (!isAuthenticated) {
        showToast('Please login to view contact details', 'info');
        window.location.href = `login.html`;
        return;
    }

    const modal = document.getElementById('contactModal');
    const body = document.getElementById('modalBody');
    
    body.innerHTML = `
        <div style="display:flex;align-items:center;gap:20px;margin-bottom:24px;">
            <div class="blood-group-badge">${donor.blood_group}</div>
            <div>
                <h4 style="font-size:1.2rem;">${donor.user.first_name} ${donor.user.last_name || ''}</h4>
                <p style="color:var(--text-secondary)">${donor.city}, ${donor.state}</p>
            </div>
        </div>
        
        <div style="background:var(--bg-primary);padding:16px;border-radius:var(--radius-md);border:1px solid var(--border-color);">
            <div style="margin-bottom:12px;">
                <span style="color:var(--text-muted);font-size:0.85rem;display:block;">Phone Number</span>
                <a href="tel:${donor.phone}" style="font-size:1.1rem;font-weight:600;color:var(--crimson-light);">${donor.phone}</a>
            </div>
            <div>
                <span style="color:var(--text-muted);font-size:0.85rem;display:block;">Email Address</span>
                <a href="mailto:${donor.user.email}" style="color:var(--text-primary);">${donor.user.email}</a>
            </div>
        </div>
    `;
    
    modal.classList.add('active');
}

function closeModal() {
    document.getElementById('contactModal').classList.remove('active');
}

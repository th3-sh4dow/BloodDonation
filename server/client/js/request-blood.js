/**
 * Request Blood Logic
 */

document.addEventListener('DOMContentLoaded', () => {
    checkAuthAndInitForm();
    loadActiveRequests();

    // Urgency styling toggle
    document.getElementById('urgency')?.addEventListener('change', function() {
        const btn = document.getElementById('submitBtn');
        if (this.value === 'emergency') {
            btn.className = 'btn btn-emergency';
            btn.innerHTML = '🚨 Submit Emergency Request';
        } else {
            btn.className = 'btn btn-primary';
            btn.innerHTML = 'Submit Request';
        }
    });
});

async function checkAuthAndInitForm() {
    await checkAuthStatus();
    if (isAuthenticated) {
        document.getElementById('loginPrompt').style.display = 'none';
        const form = document.getElementById('requestForm');
        form.style.display = 'block';

        // Pre-fill phone if available
        if (currentUser && sessionStorage.getItem('profile')) {
            try {
                const profile = JSON.parse(sessionStorage.getItem('profile'));
                if (profile.phone) document.getElementById('contactNumber').value = profile.phone;
                if (profile.city) document.getElementById('reqCity').value = profile.city;
            } catch(e) {}
        }

        form.addEventListener('submit', handleRequestSubmit);
    } else {
        document.getElementById('loginPrompt').style.display = 'block';
        document.getElementById('requestForm').style.display = 'none';
    }
}

async function handleRequestSubmit(e) {
    e.preventDefault();
    const btn = document.getElementById('submitBtn');
    const originalText = btn.innerHTML;
    btn.innerHTML = 'Submitting...';
    btn.disabled = true;

    const data = {
        patient_name: document.getElementById('patientName').value,
        blood_group_needed: document.getElementById('reqBloodGroup').value,
        units_needed: document.getElementById('unitsNeeded').value,
        hospital_name: document.getElementById('hospitalName').value,
        city: document.getElementById('reqCity').value,
        contact_number: document.getElementById('contactNumber').value,
        urgency: document.getElementById('urgency').value,
        notes: document.getElementById('notes').value
    };

    try {
        await API.createRequest(data);
        document.getElementById('successModal').classList.add('active');
        loadActiveRequests(); // Refresh list
        e.target.reset(); // Reset form
    } catch (err) {
        showToast('Failed to submit request', 'error');
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

async function loadActiveRequests() {
    const list = document.getElementById('activeRequestsList');
    try {
        const data = await API.getRequests({ status: 'open' });
        
        if (data.requests && data.requests.length > 0) {
            list.innerHTML = data.requests.slice(0, 5).map(req => `
                <div class="card" style="padding: 16px 20px;">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px;">
                        <div style="display:flex;align-items:center;gap:12px;">
                            <div class="blood-group-badge sm">${req.blood_group_needed}</div>
                            <div>
                                <h4 style="font-size:1rem;margin-bottom:2px;">${req.hospital_name}</h4>
                                <span class="urgency-tag ${req.urgency}">${req.urgency}</span>
                            </div>
                        </div>
                        <span style="font-size:1.1rem;font-weight:700;">${req.units_needed} unit(s)</span>
                    </div>
                    <div style="display:flex;justify-content:space-between;font-size:0.85rem;color:var(--text-secondary);">
                        <span>📍 ${req.city}</span>
                        <span>${timeAgo(req.created_at)}</span>
                    </div>
                </div>
            `).join('');
            
            if (data.total > 5) {
                list.innerHTML += `<div style="text-align:center;padding:10px;"><a href="/find-blood/">View all ${data.total} requests</a></div>`;
            }
        } else {
            list.innerHTML = `<div class="empty-state" style="padding:40px 20px;">No active requests right now.</div>`;
        }
    } catch(err) {
        list.innerHTML = `<div class="empty-state">Failed to load requests</div>`;
    }
}

let allComplaints = [];
let currentFilter = "All";
let myUserId = null;

async function loadMe() {
    const me = await apiFetch("/api/me");
    myUserId = me.id;
    document.getElementById("navName").textContent = me.name;
    document.getElementById("navInitial").textContent = me.name[0].toUpperCase();
    document.getElementById("subtext").textContent = `${me.department} · Semester ${me.semester} · ${me.college}`;
}

async function loadStats() {
    const s = await apiFetch("/api/stats");
    document.getElementById("statTotal").textContent = s.total;
    document.getElementById("statPending").textContent = s.pending;
    document.getElementById("statReview").textContent = s.in_review;
    document.getElementById("statResolved").textContent = s.resolved;
}

async function loadComplaints() {
    allComplaints = await apiFetch("/api/complaints");
    renderComplaints();
}

function filterComplaints(filter, btn) {
    currentFilter = filter;
    document.querySelectorAll(".filter-btn").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    renderComplaints();
}

function renderComplaints() {
    const list = document.getElementById("complaintsList");
    const isAdminPage = !!document.querySelector('.admin-page');
    let filtered = allComplaints;
    if (currentFilter === "Mine") {
        filtered = allComplaints.filter(c => c.user_id === myUserId);
    } else if (currentFilter !== "All") {
        filtered = allComplaints.filter(c => c.status === currentFilter);
    }

    if (!filtered.length) {
        list.innerHTML = `<div class="empty-state">
            <div class="empty-icon">📭</div>
            <p>No complaints found.</p>
            ${currentFilter === "All" ? '<a href="/submit" class="btn btn-primary" style="margin-top:1rem;">Submit your first complaint</a>' : ''}
        </div>`;
        return;
    }

    list.innerHTML = filtered.map(c => `
        <div class="complaint-card" onclick="openModal(${c.id})">
            <div class="c-header">
                <div class="c-title">${escHtml(c.title)} ${c.user_id === myUserId ? '<span class="mine-tag">Yours</span>' : ''}</div>
                <div class="c-badges">
                    <span class="badge ${badgeClass('status', c.status)}">${c.status}</span>
                    <span class="badge ${badgeClass('priority', c.priority)}">${c.priority}</span>
                    <span class="badge ${badgeClass('category', c.category)}">${c.category}</span>
                </div>
            </div>
            <div class="c-meta">
                <span>👤 ${escHtml(c.student_name || 'Anonymous')}</span>
                <span>📅 ${timeAgo(c.created_at)}</span>
                ${c.is_anonymous ? '<span>🔒 Anonymous</span>' : ''}
                ${c.tags?.length ? `<span>🏷 ${c.tags.slice(0,2).join(', ')}</span>` : ''}
            </div>
            <div class="c-desc">${escHtml(c.description)}</div>
            <div class="c-footer">
                <div style="font-size:0.78rem;color:var(--gray);">
                    Sentiment: <span class="badge ${badgeClass('sentiment',c.sentiment)}" style="font-size:0.68rem;">${c.sentiment}</span>
                </div>
                ${isAdminPage ? '' : `<button class="upvote-btn" onclick="upvote(event,${c.id},this)">
                    👍 <span id="upvote-${c.id}">${c.upvotes}</span>
                </button>`}
            </div>
        </div>
    `).join('');
}

async function upvote(e, id, btn) {
    e.stopPropagation();
    const data = await apiFetch(`/api/complaints/${id}/upvote`, {method:"POST"});
    const span = document.getElementById(`upvote-${id}`);
    span.textContent = parseInt(span.textContent) + (data.voted ? 1 : -1);
    btn.classList.toggle("voted", data.voted);
}

async function openModal(id) {
    const c = allComplaints.find(x => x.id === id);
    const logs = await apiFetch(`/api/complaints/${id}/activity`);
    const modal = document.getElementById("modal");
    const content = document.getElementById("modalContent");

    content.innerHTML = `
        <div class="modal-header">
            <div>
                <div style="font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:800;">${escHtml(c.title)}</div>
                <div style="display:flex;gap:0.4rem;margin-top:0.5rem;flex-wrap:wrap;">
                    <span class="badge ${badgeClass('status',c.status)}">${c.status}</span>
                    <span class="badge ${badgeClass('priority',c.priority)}">${c.priority}</span>
                    <span class="badge ${badgeClass('category',c.category)}">${c.category}</span>
                </div>
            </div>
            <button class="modal-close" onclick="closeModal()">✕</button>
        </div>

        <div style="font-size:0.875rem;line-height:1.6;color:#444;margin-bottom:1rem;">
            ${escHtml(c.description)}
        </div>

        <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.5rem;font-size:0.8rem;margin-bottom:1rem;">
            <div><span style="color:var(--gray);">Submitted by:</span> ${escHtml(c.student_name || 'Anonymous')}</div>
            <div><span style="color:var(--gray);">Submitted:</span> ${new Date(c.created_at).toLocaleDateString('en-GB')}</div>
            <div><span style="color:var(--gray);">Sentiment:</span> ${c.sentiment} (${c.sentiment_score})</div>
            ${c.assigned_to ? `<div><span style="color:var(--gray);">Assigned to:</span> ${c.assigned_to}</div>` : ''}
            ${c.resolved_at ? `<div><span style="color:var(--gray);">Resolved:</span> ${new Date(c.resolved_at).toLocaleDateString('en-GB')}</div>` : ''}
        </div>

        ${c.admin_response ? `
        <div class="admin-response-box">
            <div style="font-size:0.75rem;font-weight:600;color:var(--blue);margin-bottom:0.3rem;">ADMIN RESPONSE</div>
            ${escHtml(c.admin_response)}
        </div>` : ''}

        ${document.querySelector('.admin-page') ? `
        <div class="admin-edit-box" style="border-top:1px solid var(--border);margin-top:1.25rem;padding-top:1.25rem;">
            <div style="font-family:'Manrope',sans-serif;font-size:0.8rem;font-weight:800;text-transform:uppercase;letter-spacing:0.06em;color:var(--gray);margin-bottom:0.8rem;">Manage Complaint</div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.75rem;">
                <label class="form-group" style="margin-bottom:0;">
                    <span class="form-label">Status</span>
                    <select id="adminStatus" class="form-select">
                        ${['Pending', 'In Review', 'Resolved', 'Rejected'].map(status => `<option${c.status === status ? ' selected' : ''}>${status}</option>`).join('')}
                    </select>
                </label>
                <label class="form-group" style="margin-bottom:0;">
                    <span class="form-label">Assign To</span>
                    <input id="adminAssignee" class="form-input" type="text" value="${escHtml(c.assigned_to || '')}" placeholder="Department or staff name">
                </label>
            </div>
            <label class="form-group" style="display:block;margin-top:0.75rem;margin-bottom:0.75rem;">
                <span class="form-label">Admin Response</span>
                <textarea id="adminResponse" class="form-textarea" rows="3" placeholder="Write an update for the student...">${escHtml(c.admin_response || '')}</textarea>
            </label>
            <button class="btn btn-primary" onclick="saveComplaint(${c.id})">Save Changes</button>
        </div>` : ''}

        <div style="font-family:'Syne',sans-serif;font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:var(--gray);margin-top:1.25rem;margin-bottom:0.5rem;">
            Activity Timeline
        </div>
        <div class="timeline">
            ${logs.map(l => `
                <div class="tl-item">
                    <div class="tl-dot"></div>
                    <div><strong>${l.action}</strong> by ${l.performed_by}</div>
                    ${l.note ? `<div style="color:#555;margin-top:0.2rem;">${escHtml(l.note)}</div>` : ''}
                    <div class="tl-time">${timeAgo(l.created_at)}</div>
                </div>
            `).join('') || '<div style="color:var(--gray);font-size:0.85rem;">No activity yet</div>'}
        </div>
    `;

    modal.classList.add("open");
}

async function saveComplaint(id) {
    const data = await apiFetch(`/api/complaints/${id}`, {
        method: "PATCH",
        body: {
            status: document.getElementById("adminStatus").value,
            assigned_to: document.getElementById("adminAssignee").value.trim(),
            admin_response: document.getElementById("adminResponse").value.trim()
        }
    });

    if (data.error) {
        toast(data.error, "error");
        return;
    }

    const complaint = allComplaints.find(item => item.id === id);
    complaint.status = document.getElementById("adminStatus").value;
    complaint.assigned_to = document.getElementById("adminAssignee").value.trim();
    complaint.admin_response = document.getElementById("adminResponse").value.trim();
    toast("Complaint updated successfully", "success");
    closeModal();
    renderComplaints();
    await loadStats();
}

function closeModal() { document.getElementById("modal").classList.remove("open"); }
document.getElementById("modal").addEventListener("click", function(e) {
    if (e.target === this) closeModal();
});

function escHtml(s) {
    return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

async function logout() {
    await apiFetch("/api/logout", {method:"POST"});
    window.location = "/login";
}

// Init
loadMe().then(loadComplaints);
loadStats();

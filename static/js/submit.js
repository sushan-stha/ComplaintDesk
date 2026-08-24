let anonMode = false;
let previewTimer = null;

function toggleAnon() {
    anonMode = !anonMode;
    const sw = document.getElementById("anonSwitch");
    sw.classList.toggle("on", anonMode);
}

function schedulePreview() {
    clearTimeout(previewTimer);
    previewTimer = setTimeout(fetchPreview, 600);
}

async function fetchPreview() {
    const title = document.getElementById("title").value.trim();
    const desc = document.getElementById("description").value.trim();
    if (!title && !desc) return;

    const preview = document.getElementById("aiPreview");
    const content = document.getElementById("aiContent");
    content.innerHTML = '<span class="spinner" style="border-top-color:var(--blue);border-color:var(--border);"></span>';

    const data = await apiFetch("/api/classify", {
        method: "POST", body: {title, description: desc}
    });

    preview.classList.add("active");
    content.innerHTML = `
        <div class="ai-row">
            <span class="ai-key">Category</span>
            <span class="badge ${badgeClass('category', data.category)}">${data.category}</span>
        </div>
        <div class="ai-row">
            <span class="ai-key">Priority</span>
            <span class="badge ${badgeClass('priority', data.priority)}">${data.priority}</span>
        </div>
        <div class="ai-row">
            <span class="ai-key">Sentiment</span>
            <span class="badge ${badgeClass('sentiment', data.sentiment)}">${data.sentiment}</span>
        </div>
        <div style="margin-top:0.75rem;">
            <div style="font-size:0.75rem;color:var(--gray);margin-bottom:0.3rem;">
                Confidence: ${Math.round(data.confidence * 100)}%
            </div>
            <div class="confidence-bar">
                <div class="confidence-fill" style="width:${data.confidence*100}%"></div>
            </div>
        </div>
        ${data.tags.length ? `
        <div class="tags-wrap">
            ${data.tags.map(t => `<span class="tag-pill">#${t}</span>`).join('')}
        </div>` : ''}
    `;
}

async function submitComplaint() {
    const title = document.getElementById("title").value.trim();
    const description = document.getElementById("description").value.trim();

    if (!title || !description) { toast("Please fill in both title and description", "error"); return; }
    if (description.length < 20) { toast("Please provide a more detailed description", "error"); return; }

    const btn = document.getElementById("submitBtn");
    btn.innerHTML = '<span class="spinner"></span> Submitting...'; btn.disabled = true;

    const data = await apiFetch("/api/complaints", {
        method: "POST",
        body: { title, description, anonymous: anonMode }
    });

    if (data.error) {
        toast(data.error, "error"); btn.innerHTML = "🚀 Submit Complaint"; btn.disabled = false;
    } else {
        toast("Complaint submitted successfully!", "success");
        setTimeout(() => window.location = "/dashboard", 1200);
    }
}

async function logout() {
    await apiFetch("/api/logout", {method:"POST"});
    window.location = "/login";
}

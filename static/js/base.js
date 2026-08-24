function toast(msg, type="info") {
        const t = document.getElementById("toast");
        t.textContent = msg;
        t.className = `show ${type}`;
        setTimeout(() => t.className = "", 3000);
    }

    async function apiFetch(url, opts={}) {
        const res = await fetch(url, {
            headers: {"Content-Type": "application/json"},
            ...opts,
            body: opts.body ? JSON.stringify(opts.body) : undefined
        });
        return res.json();
    }

    function badgeClass(type, value) {
        const map = {
            category: {
                Academic:"badge-academic", Hostel:"badge-hostel",
                Transport:"badge-transport", Infrastructure:"badge-infra",
                Administration:"badge-admin", Other:"badge-other"
            },
            priority: { Critical:"badge-critical", High:"badge-high", Medium:"badge-medium", Low:"badge-low" },
            status: { Pending:"badge-pending", "In Review":"badge-in-review", Resolved:"badge-resolved", Rejected:"badge-rejected" },
            sentiment: { Positive:"badge-low", Neutral:"badge-other", Negative:"badge-medium", "Very Negative":"badge-critical" }
        };
        return map[type]?.[value] || "badge-other";
    }

    function timeAgo(dateStr) {
        const diff = Date.now() - new Date(dateStr);
        const m = Math.floor(diff/60000);
        if (m < 1) return "just now";
        if (m < 60) return `${m}m ago`;
        const h = Math.floor(m/60);
        if (h < 24) return `${h}h ago`;
        return `${Math.floor(h/24)}d ago`;
    }

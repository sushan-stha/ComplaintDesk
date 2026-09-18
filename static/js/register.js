async function register() {
    const btn = document.getElementById("regBtn");
    const name = document.getElementById("rName").value.trim();
    const email = document.getElementById("rEmail").value.trim();
    const pass = document.getElementById("rPass").value;

    if (!name || !email || !pass) { toast("Please fill all fields", "error"); return; }
    if (!/^[A-Za-z]+(?:\s+[A-Za-z]+)*$/.test(name)) {
        toast("Name can contain letters and spaces only", "error"); return;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        toast("Please enter a valid email address", "error"); return;
    }
    if (pass.length < 8) { toast("Password must be at least 8 characters", "error"); return; }
    if (!/[A-Z]/.test(pass)) { toast("Password must contain at least one capital letter", "error"); return; }
    if (!/[^A-Za-z0-9]/.test(pass)) { toast("Password must contain at least one special character", "error"); return; }

    btn.innerHTML = '<span class="spinner"></span> Creating...'; btn.disabled = true;

    const data = await apiFetch("/api/register", {
        method: "POST",
        body: {
            name, email, password: pass,
            college: document.getElementById("rCollege").value,
            department: document.getElementById("rDept").value,
            semester: parseInt(document.getElementById("rSem").value)
        }
    });

    if (data.error) {
        toast(data.error, "error"); btn.innerHTML = "Create Account"; btn.disabled = false;
    } else {
        toast("Account created! Redirecting...", "success");
        setTimeout(() => window.location = "/login", 1000);
    }
}

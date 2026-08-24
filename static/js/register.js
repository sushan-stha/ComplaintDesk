async function register() {
    const btn = document.getElementById("regBtn");
    const name = document.getElementById("rName").value.trim();
    const email = document.getElementById("rEmail").value.trim();
    const pass = document.getElementById("rPass").value;

    if (!name || !email || !pass) { toast("Please fill all fields", "error"); return; }
    if (pass.length < 6) { toast("Password must be at least 6 characters", "error"); return; }

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

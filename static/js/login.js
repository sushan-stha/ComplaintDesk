function fillCred(email, pass) {
    document.getElementById("loginEmail").value = email;
    document.getElementById("loginPassword").value = pass;
}

async function login() {
    const btn = document.getElementById("loginBtn");
    btn.innerHTML = '<span class="spinner"></span> Signing in...';
    btn.disabled = true;

    const data = await apiFetch("/api/login", {
        method: "POST",
        body: {
            email: document.getElementById("loginEmail").value,
            password: document.getElementById("loginPassword").value
        }
    });

    if (data.error) {
        toast(data.error, "error");
        btn.innerHTML = "Sign In"; btn.disabled = false;
    } else {
        toast(`Welcome, ${data.name}!`, "success");
        setTimeout(() => window.location = data.redirect, 800);
    }
}

document.addEventListener("keydown", e => { if(e.key === "Enter") login(); });

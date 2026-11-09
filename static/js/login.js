function fillCred(email, pass) {
    document.getElementById("loginEmail").value = email;
    document.getElementById("loginPassword").value = pass;
}

function togglePassword() {
    const password = document.getElementById("loginPassword");
    const toggle = document.getElementById("passwordToggle");
    const isHidden = password.type === "password";

    password.type = isHidden ? "text" : "password";
    toggle.innerHTML = "&#128065;";
    toggle.setAttribute("aria-label", isHidden ? "Hide password" : "Show password");
}

const password = document.getElementById("loginPassword");
const passwordField = document.createElement("div");
passwordField.style.cssText = "position:relative;";
password.parentNode.insertBefore(passwordField, password);
passwordField.appendChild(password);
password.style.paddingRight = "4.5rem";

const passwordToggle = document.createElement("button");
passwordToggle.type = "button";
passwordToggle.id = "passwordToggle";
passwordToggle.className = "password-toggle";
passwordToggle.innerHTML = "&#128065;";
passwordToggle.setAttribute("aria-label", "Show password");
passwordToggle.setAttribute("onclick", "togglePassword()");
passwordToggle.style.cssText = "position:absolute;top:0;right:0;bottom:0;width:3rem;display:flex;align-items:center;justify-content:center;border:0;border-radius:0 7px 7px 0;background:transparent;color:#000;cursor:pointer;font:600 0.8rem 'Nunito Sans',sans-serif;padding:0 0.25rem;line-height:1;appearance:none;";
const passwordToggleStyles = document.createElement("style");
passwordToggleStyles.textContent = ".password-toggle:hover, .password-toggle:focus-visible, .password-toggle:active { background:#EEF2FF; color:#000; }";
document.head.appendChild(passwordToggleStyles);
passwordField.appendChild(passwordToggle);

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

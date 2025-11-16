console.log("auth.js loaded");

// ---------------- SIGNUP ----------------
const signupForm = document.getElementById("signupForm");

if (signupForm) {
    signupForm.addEventListener("submit", async (e) => {
        e.preventDefault();

    const API_URL = "http://localhost:5500/api/auth";

// ---------------- SIGNUP -----------------
async function handleSignup() {
  const name = document.getElementById("name").value;
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  const res = await fetch(`${API_URL}/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, email, password })
  });

  const data = await res.json();

  if (!res.ok) {
    return alert(data.message || "Signup failed");
  }

  alert("Signup Successful!");
  window.location.href = "/frontend/login.html";
}

// ---------------- LOGIN -----------------
async function handleLogin() {
  const email = document.getElementById("loginEmail").value;
  const password = document.getElementById("loginPassword").value;

  const res = await fetch(`${API_URL}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password })
  });

  const data = await res.json();

  if (!res.ok) {
    return alert(data.message || "Login failed");
  }

  // Save token
  localStorage.setItem("token", data.token);

  alert("Login successful!");

  // 🔥 Redirect to Dashboard
  window.location.href = "/frontend/dashboard.html";
}
    const name = document.getElementById("name").value.trim();
        const email = document.getElementById("email").value.trim();
        const password = document.getElementById("password").value.trim();

        try {
            const res = await fetch("http://localhost:5500/api/auth/register", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ name, email, password }),
            });

            const data = await res.json();
            console.log("Signup Response:", data);

            if (res.ok) {
                alert("Signup successful! Redirecting to login...");
                window.location.href = "login.html";
            } else {
                alert(data.message || "Signup failed!");
            }
        } catch (error) {
            console.error(error);
            alert("Error connecting to server");
        }
    });
}


// ---------------- LOGIN ----------------
const loginForm = document.getElementById("loginForm");

if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const email = document.getElementById("email").value.trim();
        const password = document.getElementById("password").value.trim();

        try {
            const res = await fetch("http://localhost:5500/api/auth/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password }),
            });

            const data = await res.json();
            console.log("Login Response:", data);

            if (res.ok && data.token) {
                localStorage.setItem("authToken", data.token);
                alert("Login successful!");
                window.location.href = "dashboard.html";
            } else {
                alert(data.message || "Login failed!");
            }
        } catch (error) {
            console.error(error);
            alert("Error connecting to server");
        }
    });
}

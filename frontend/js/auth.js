console.log("auth.js loaded");

// API BASE URL
const API_URL = "http://127.0.0.1:5500/api/auth";

// Toast / message box
function showMessage(msg, type = "error") {
  let box = document.getElementById("msgBox");
  if (!box) {
    box = document.createElement("div");
    box.id = "msgBox";
    box.style.position = "fixed";
    box.style.top = "20px";
    box.style.right = "20px";
    box.style.padding = "12px 18px";
    box.style.borderRadius = "6px";
    box.style.zIndex = "9999";
    box.style.color = "#fff";
    box.style.fontWeight = "600";
    document.body.appendChild(box);
  }

  box.style.background = type === "success" ? "#28a745" : "#d9534f";
  box.innerText = msg;
  box.style.display = "block";

  setTimeout(() => (box.style.display = "none"), 2500);
}


// ---------- AUTH PROTECTED PAGE CHECK ----------
const publicPages = ["login.html", "signup.html"];
const currentPage = location.pathname.split("/").pop();
const authToken = localStorage.getItem("authToken");

if (!publicPages.includes(currentPage) && (!authToken || authToken === "null" || authToken === "undefined")) {
  window.location.href = "login.html";
}


// ---------- SIGNUP ----------
const signupForm = document.getElementById("signupForm");

if (signupForm) {
  signupForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const name = document.getElementById("name").value.trim();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();

    try {
      const res = await fetch(`${API_URL}/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email, password }),
      });

      const data = await res.json();
      if (!res.ok) return showMessage(data.message || "Signup failed");

      showMessage("Account created successfully!", "success");
      setTimeout(() => (window.location.href = "login.html"), 1400);
    } catch {
      showMessage("Error connecting to server");
    }
  });
}


// ---------- LOGIN ----------
const loginForm = document.getElementById("loginForm");

if (loginForm) {
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();

    try {
      const res = await fetch(`${API_URL}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();
      if (!res.ok || !data.token)
        return showMessage(data.message || "Invalid credentials");

      // SAVE TOKEN — LocalStorage (correct for protected dashboard pages)
      localStorage.setItem("authToken", data.token);

      showMessage("Login successful! Redirecting...", "success");
      setTimeout(() => (window.location.href = "index.html"), 1200);
    } catch {
      showMessage("Error connecting to server");
    }
  });
}


// ---------- LOGOUT ----------
window.logout = function () {
  localStorage.removeItem("authToken");
  window.location.href = "login.html";
};

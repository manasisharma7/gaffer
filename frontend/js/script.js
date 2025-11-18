// NAVBAR COLOR CHANGE ON SCROLL
window.addEventListener("scroll", () => {
  const nav = document.querySelector(".navbar");
  nav.classList.toggle("scrolled", window.scrollY > 50);
});

// CONTACT FORM MESSAGE (FRONTEND ONLY)
const form = document.getElementById("contactForm");

if (form) {
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const name = document.getElementById("name").value.trim();
    const email = document.getElementById("email").value.trim();
    const message = document.getElementById("message").value.trim();

    if (!name || !email || !message) {
      alert("Please fill out all fields before submitting.");
    } else {
      alert("Message sent successfully! We’ll get back to you soon.");
      form.reset();
    }
  });
}

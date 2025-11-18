console.log("player-performance.js loaded");

// Backend URLs
const ANALYSIS_API_URL =
  "http://127.0.0.1:5500/api/analysis/player-performance";
const IMAGES_API_URL =
  "http://127.0.0.1:5500/api/analysis/player-performance/images";

const runBtn = document.getElementById("runModelBtn");
const resultsContainer = document.getElementById("results");

function showMessage(msg) {
  alert(msg);
}

if (runBtn && resultsContainer) {
  runBtn.addEventListener("click", async () => {
    console.log("Run button clicked");

    const token =
      sessionStorage.getItem("authToken") || localStorage.getItem("authToken");

    if (!token) {
      showMessage("Please login first.");
      return;
    }

    runBtn.disabled = true;
    runBtn.innerText = "⏳ Running AI Model... Please wait";
    resultsContainer.innerHTML =
      "<p style='text-align:center'>⏳ Running analysis... please wait...</p>";

    try {
      // Run the model backend
      const res = await fetch(ANALYSIS_API_URL, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      const data = await res.json();
      console.log("API Response:", data);

      if (!res.ok) throw new Error(data.message || "Model error");

      // Get image URLs
      const imgRes = await fetch(IMAGES_API_URL);
      const imgData = await imgRes.json();
      console.log("Images:", imgData);

      const images = imgData.images || [];
      if (images.length === 0) {
        resultsContainer.innerHTML =
          "<p style='text-align:center;color:#ff6b6b'>No graphs generated.</p>";
        runBtn.innerText = "🚀 Run Player Performance Model";
        runBtn.disabled = false;
        return;
      }

      // Display in grid layout
      let html = `
  <div style="display:flex;flex-wrap:wrap;gap:25px;justify-content:center;align-items:center;">
`;

      images.forEach((url) => {
        html += `
    <div style="background:#040814;padding:12px;border-radius:14px;
                box-shadow:0 0 12px rgba(0,255,200,0.3);width:420px;">
      <img src="http://127.0.0.1:5500${url}" 
           style="width:100%;border-radius:10px;display:block;">
    </div>
    `;
      });

      html += "</div>";
      resultsContainer.innerHTML = html;


      runBtn.innerText = "✔ Model Completed – Run Again";
    } catch (err) {
      console.error(err);
      showMessage("⚠ Error: " + err.message);
      resultsContainer.innerHTML =
        "<p style='text-align:center;color:#ff6b6b'>Error running model.</p>";
      runBtn.innerText = "🚀 Run Player Performance Model";
    }

    runBtn.disabled = false;
  });
} else {
  console.warn("runModelBtn OR results container missing in HTML");
}

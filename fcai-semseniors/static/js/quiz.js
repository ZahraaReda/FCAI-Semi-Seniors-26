/* quiz.js — question carousel, answer tracking, submit, result display */

(function () {
  const DEPT_INFO = {
    CS: { icon: "💻", name: "Computer Science",        color: "#6C63FF" },
    AI: { icon: "🤖", name: "Artificial Intelligence", color: "#FF6584" },
    MP: { icon: "📱", name: "Mobile Programming",      color: "#43B89C" },
    MI: { icon: "🏥", name: "Medical Informatics",      color: "#F9A825" },
  };

  const slides     = document.querySelectorAll(".question-slide:not(.result-slide)");
  const resultSlide= document.getElementById("resultSlide");
  const progressBar= document.getElementById("progressBar");
  const qNumEl     = document.getElementById("qNum");

  const container  = document.querySelector(".quiz-container");
  const TOTAL_Q    = parseInt(container.dataset.total);
  const SUBMIT_URL = container.dataset.submitUrl;

  let current = 0;
  const answers = {}; // { qid: optionIndex }

  // ── Show a specific slide ─────────────────────────────────────────
  function showSlide(index) {
    slides.forEach((s, i) => {
      s.classList.toggle("active", i === index);
    });
    const pct = Math.round((index / slides.length) * 100);
    progressBar.style.width = pct + "%";
    qNumEl.textContent = index + 1;
  }

  // ── Handle option click ───────────────────────────────────────────
  document.querySelectorAll(".option-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const qid = btn.dataset.qid;
      const idx = parseInt(btn.dataset.idx);

      // Mark selected in this slide
      const slide = btn.closest(".question-slide");
      slide.querySelectorAll(".option-btn").forEach(b => b.classList.remove("selected"));
      btn.classList.add("selected");

      answers[qid] = idx;

      // Short delay then advance
      setTimeout(() => {
        if (current < slides.length - 1) {
          current++;
          showSlide(current);
        } else {
          submitQuiz();
        }
      }, 320);
    });
  });

  // ── Submit answers to backend ─────────────────────────────────────
  async function submitQuiz() {
    // Show result slide (loading state)
    slides.forEach(s => s.classList.remove("active"));
    resultSlide.classList.add("active");
    progressBar.style.width = "100%";
    document.getElementById("resultIcon").textContent  = "⏳";
    document.getElementById("resultTitle").textContent = "Calculating...";
    document.getElementById("resultDesc").textContent  = "";

    try {
      const res  = await fetch(SUBMIT_URL, {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify(answers),
      });
      const data = await res.json();
      showResult(data);
    } catch (err) {
      document.getElementById("resultTitle").textContent = "Something went wrong";
      document.getElementById("resultDesc").textContent  = "Please try again.";
    }
  }

  // ── Render result ─────────────────────────────────────────────────
  function showResult(data) {
    const dept   = data.department;
    const info   = DEPT_INFO[dept] || { icon: "🎓", name: dept, color: "#5b8cff" };
    const scores = data.scores || {};

    document.getElementById("resultIcon").textContent  = info.icon;
    document.getElementById("resultTitle").textContent = info.name;
    document.getElementById("resultDesc").textContent  =
      `Based on your answers, ${info.name} is your best fit for next year!`;

    // Score bars
    const maxScore = Math.max(...Object.values(scores), 1);
    const barsEl   = document.getElementById("scoreBars");
    barsEl.innerHTML = "";

    Object.entries(scores).forEach(([key, val]) => {
      const pct = Math.round((val / maxScore) * 100);
      const row = document.createElement("div");
      row.className = "score-row";
      row.innerHTML = `
        <span class="score-label">${key}</span>
        <div class="score-track">
          <div class="score-fill dept-${key.toLowerCase()}" style="width:0%"
               data-target="${pct}"></div>
        </div>
      `;
      barsEl.appendChild(row);
    });

    // Animate bars after brief delay
    setTimeout(() => {
      document.querySelectorAll(".score-fill").forEach(fill => {
        fill.style.width = fill.dataset.target + "%";
      });
    }, 150);

    // Color the result icon with dept color
    document.getElementById("resultIcon").style.filter =
      `drop-shadow(0 0 20px ${info.color}80)`;
  }

  // ── Init ──────────────────────────────────────────────────────────
  showSlide(0);
})();
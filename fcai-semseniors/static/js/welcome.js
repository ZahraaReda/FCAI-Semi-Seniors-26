/* welcome.js — typewriter effect + particle canvas + navigation */

(function () {
  const TEXT     = "FCAI Semi Seniors 26'";
  const SPEED_MS = 80;
  const el       = document.getElementById("typewriter");
  const hint     = document.getElementById("enterHint");
  const wrapper  = document.getElementById("welcomeClick");

  let idx = 0, done = false;

  function type() {
    if (idx <= TEXT.length) {
      el.textContent = TEXT.slice(0, idx);
      idx++;
      setTimeout(type, idx === 1 ? 600 : SPEED_MS);
    } else {
      done = true;
      hint.style.opacity = "1";
    }
  }

  setTimeout(type, 800);

  // Navigate on click / Enter
  function navigate() {
    wrapper.style.pointerEvents = "none";
    document.querySelector(".welcome-bg").classList.add("exit");
    setTimeout(() => { window.location.href = "/gallery"; }, 480);
  }

  wrapper.addEventListener("click", navigate);
  document.addEventListener("keydown", e => {
    if (e.key === "Enter" || e.key === " ") navigate();
  });

  // ── Particle Canvas ───────────────────────────────────────────────
  const canvas = document.getElementById("particles");
  const ctx    = canvas.getContext("2d");

  function resize() {
    canvas.width  = window.innerWidth;
    canvas.height = window.innerHeight;
  }
  resize();
  window.addEventListener("resize", resize);

  const PARTICLE_COUNT = 60;
  const particles = Array.from({ length: PARTICLE_COUNT }, () => ({
    x:  Math.random() * window.innerWidth,
    y:  Math.random() * window.innerHeight,
    vx: (Math.random() - 0.5) * 0.4,
    vy: (Math.random() - 0.5) * 0.4,
    r:  Math.random() * 1.8 + 0.5,
    a:  Math.random() * 0.5 + 0.1,
  }));

  function drawParticles() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    particles.forEach(p => {
      p.x += p.vx;
      p.y += p.vy;
      if (p.x < 0) p.x = canvas.width;
      if (p.x > canvas.width) p.x = 0;
      if (p.y < 0) p.y = canvas.height;
      if (p.y > canvas.height) p.y = 0;

      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(91,140,255,${p.a})`;
      ctx.fill();
    });

    // Draw connecting lines
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 120) {
          ctx.beginPath();
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.strokeStyle = `rgba(91,140,255,${0.06 * (1 - dist / 120)})`;
          ctx.lineWidth = 1;
          ctx.stroke();
        }
      }
    }

    requestAnimationFrame(drawParticles);
  }

  drawParticles();
})();
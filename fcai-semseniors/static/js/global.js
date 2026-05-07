/* global.js — shared utilities */

// Auto-dismiss toasts
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".toast").forEach(t => {
    setTimeout(() => {
      t.style.transition = "opacity 0.4s";
      t.style.opacity = "0";
      setTimeout(() => t.remove(), 400);
    }, 3500);
  });
});
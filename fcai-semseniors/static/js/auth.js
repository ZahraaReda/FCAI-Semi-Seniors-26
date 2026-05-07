/* auth.js — form input focus effects */

document.addEventListener("DOMContentLoaded", () => {
  // Add floating label animation if desired in future
  const inputs = document.querySelectorAll("input");
  inputs.forEach(inp => {
    inp.addEventListener("focus",  () => inp.parentElement.classList.add("focused"));
    inp.addEventListener("blur",   () => inp.parentElement.classList.remove("focused"));
  });
});
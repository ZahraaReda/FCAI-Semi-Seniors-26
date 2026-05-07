/* gallery.js — department filter + stagger animation */

(function () {
  const filterBtns = document.querySelectorAll(".filter-btn");
  const cards      = document.querySelectorAll(".card");

  // Stagger card entrance
  cards.forEach((c, i) => {
    c.style.animationDelay = `${i * 0.05}s`;
  });

  filterBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      filterBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");

      const dept = btn.dataset.dept;

      cards.forEach(card => {
        if (dept === "all" || card.dataset.dept === dept) {
          card.classList.remove("hidden");
        } else {
          card.classList.add("hidden");
        }
      });
    });
  });
})();
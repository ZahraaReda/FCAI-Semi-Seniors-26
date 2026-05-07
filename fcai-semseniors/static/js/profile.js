/* profile.js — live photo preview + character counter */

(function () {
  // ── Photo preview ────────────────────────────────────────────────
  const photoInput   = document.getElementById("photoInput");
  const photoPreview = document.getElementById("photoPreview");
  const photoLabel   = document.querySelector(".photo-label");

  photoInput.addEventListener("change", () => {
    const file = photoInput.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      // Replace whatever is inside the preview with a fresh <img>
      photoPreview.innerHTML = `
        <img src="${e.target.result}" alt="Preview"
             style="width:100%;height:100%;object-fit:cover;" />
      `;
      if (photoLabel) photoLabel.textContent = "Change Photo";
    };
    reader.readAsDataURL(file);
  });

  // ── Senior quote character counter ───────────────────────────────
  const quoteArea = document.getElementById("senior_quote");
  const quoteLenEl= document.getElementById("quoteLen");

  if (quoteArea && quoteLenEl) {
    // Set initial count (for edit mode when value is pre-filled)
    quoteLenEl.textContent = quoteArea.value.length;

    quoteArea.addEventListener("input", () => {
      const len = quoteArea.value.length;
      quoteLenEl.textContent = len;
      // Warn when close to limit
      quoteLenEl.style.color = len > 180 ? "#FF6584" : "";
    });
  }

  // ── Drag-and-drop photo upload ───────────────────────────────────
  const uploadArea = document.getElementById("photoArea");

  if (uploadArea) {
    uploadArea.addEventListener("dragover", (e) => {
      e.preventDefault();
      uploadArea.style.opacity = "0.7";
    });
    uploadArea.addEventListener("dragleave", () => {
      uploadArea.style.opacity = "1";
    });
    uploadArea.addEventListener("drop", (e) => {
      e.preventDefault();
      uploadArea.style.opacity = "1";
      const file = e.dataTransfer.files[0];
      if (file && file.type.startsWith("image/")) {
        // Transfer the file to the hidden input
        const dt = new DataTransfer();
        dt.items.add(file);
        photoInput.files = dt.files;
        photoInput.dispatchEvent(new Event("change"));
      }
    });
  }
})();

  // ── Department card selection highlight ──────────────────────────
  const deptCards = document.querySelectorAll(".dept-card");
  deptCards.forEach(card => {
    card.addEventListener("click", () => {
      deptCards.forEach(c => c.classList.remove("selected"));
      card.classList.add("selected");
    });
  });
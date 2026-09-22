/**
 * Upload Module for Duplicate Record Detection
 * Manages drag & drop, file selection, uploads, and active file cards.
 */

window.UploadManager = (function () {
  let dropZone = null;
  let fileInput = null;
  let fileCardsContainer = null;
  let activeFileCountEl = null;

  function init() {
    dropZone = document.getElementById("drop-zone");
    fileInput = document.getElementById("file-input");
    fileCardsContainer = document.getElementById("uploaded-file-cards");
    activeFileCountEl = document.getElementById("active-file-count");

    if (!dropZone || !fileInput) return;

    dropZone.addEventListener("click", () => fileInput.click());

    dropZone.addEventListener("dragover", (e) => {
      e.preventDefault();
      dropZone.classList.add("dragover");
    });

    dropZone.addEventListener("dragleave", () => {
      dropZone.classList.remove("dragover");
    });

    dropZone.addEventListener("drop", (e) => {
      e.preventDefault();
      dropZone.classList.remove("dragover");
      if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        handleFiles(e.dataTransfer.files);
      }
    });

    fileInput.addEventListener("change", (e) => {
      if (e.target.files && e.target.files.length > 0) {
        handleFiles(e.target.files);
      }
    });

    const clearBtn = document.getElementById("btn-clear-files");
    if (clearBtn) {
      clearBtn.addEventListener("click", () => {
        window.App.resetState();
      });
    }
  }

  async function handleFiles(fileList) {
    const formData = new FormData();
    for (let i = 0; i < fileList.length; i++) {
      formData.append("files", fileList[i]);
    }

    window.App.showNotification("Uploading and parsing files...", "info");

    try {
      const response = await fetch("/api/upload", {
        method: "POST",
        body: formData,
      });
      const data = await response.json();

      if (data.success) {
        renderFileCards(data.files_added || []);
        if (data.errors && data.errors.length > 0) {
          const errMsgs = data.errors.map(e => `${e.filename}: ${e.error}`).join("; ");
          window.App.showNotification(`Uploaded with warnings: ${errMsgs}`, "warning");
        } else {
          window.App.showNotification(`Successfully added ${data.files_added.length} file(s). Click 'Run Analysis' to process.`, "success");
        }
        window.App.fetchDashboardSummary();
      } else {
        window.App.showNotification(data.error || "File upload failed.", "error");
      }
    } catch (err) {
      window.App.showNotification("Error uploading files: " + err.message, "error");
    }
  }

  function renderFileCards(files) {
    if (!fileCardsContainer) return;
    fileCardsContainer.innerHTML = "";

    if (!files || files.length === 0) {
      fileCardsContainer.innerHTML = '<div class="empty-state">No files uploaded yet. Drag files above or click to select.</div>';
      if (activeFileCountEl) activeFileCountEl.textContent = "0";
      return;
    }

    if (activeFileCountEl) activeFileCountEl.textContent = files.length;

    files.forEach((f) => {
      const card = document.createElement("div");
      card.className = "file-card";
      card.innerHTML = `
        <div class="file-card-details">
          <div class="file-card-name">${escapeHtml(f.filename)}</div>
          <div class="file-card-meta">${f.format} &bull; ${f.size_kb} KB</div>
        </div>
        <button class="btn btn-sm btn-danger remove-file-btn" data-filename="${escapeHtml(f.filename)}" title="Remove file">&times;</button>
      `;
      fileCardsContainer.appendChild(card);
    });

    // Attach remove handlers
    fileCardsContainer.querySelectorAll(".remove-file-btn").forEach((btn) => {
      btn.addEventListener("click", async (e) => {
        const fname = e.target.getAttribute("data-filename");
        await removeFile(fname);
      });
    });
  }

  async function removeFile(filename) {
    try {
      const res = await fetch("/api/upload/remove", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ filename }),
      });
      const data = await res.json();
      if (data.success) {
        window.App.showNotification(`Removed ${filename}`, "info");
        window.App.fetchDashboardSummary();
      }
    } catch (err) {
      window.App.showNotification("Failed to remove file: " + err.message, "error");
    }
  }

  function escapeHtml(str) {
    return String(str || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  return {
    init,
    renderFileCards,
  };
})();

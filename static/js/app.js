/**
 * Main Application Orchestrator
 * Anna University Regulation 2025 Data Structures Project.
 */

window.App = (function () {
  let notificationTimeout = null;

  function init() {
    setupTabs();
    setupGlobalButtons();
    setupModal();

    window.UploadManager.init();
    window.DashboardManager.init();
    window.VisualizationManager.init();

    // Initial fetch of status or sample
    fetchDashboardSummary();
  }

  function setupTabs() {
    const tabButtons = document.querySelectorAll(".tab-btn");
    tabButtons.forEach((btn) => {
      btn.addEventListener("click", () => {
        const tabName = btn.getAttribute("data-tab");
        switchToTab(tabName);
      });
    });
  }

  function switchToTab(tabName) {
    document.querySelectorAll(".tab-btn").forEach((b) => {
      b.classList.toggle("active", b.getAttribute("data-tab") === tabName);
    });

    document.querySelectorAll(".tab-content").forEach((sec) => {
      sec.classList.toggle("active", sec.id === `view-${tabName}`);
    });

    // Refresh tab content when selected
    if (tabName === "duplicates") {
      window.DashboardManager.fetchDuplicateGroups();
    } else if (tabName === "unique") {
      window.DashboardManager.fetchUniqueRecords();
    } else if (tabName === "raw") {
      window.DashboardManager.fetchRawRecords();
    } else if (tabName === "visualization") {
      window.VisualizationManager.fetchHashTableState();
    }
  }

  function setupGlobalButtons() {
    // Run analysis button
    const runBtn = document.getElementById("btn-run-analysis");
    if (runBtn) {
      runBtn.addEventListener("click", runAnalysis);
    }

    // Load sample button
    const loadSampleBtn = document.getElementById("btn-load-sample");
    if (loadSampleBtn) {
      loadSampleBtn.addEventListener("click", loadSampleData);
    }

    // Reset button
    const resetBtn = document.getElementById("btn-reset");
    if (resetBtn) {
      resetBtn.addEventListener("click", resetState);
    }
  }

  async function runAnalysis() {
    const algoSelect = document.getElementById("select-algorithm");
    const capSelect = document.getElementById("select-capacity");

    const algorithm = algoSelect ? algoSelect.value : "polynomial";
    const initial_capacity = capSelect ? parseInt(capSelect.value, 10) : 101;

    showNotification("Executing duplicate record detection via separate chaining hashing...", "info");

    try {
      const res = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ algorithm, initial_capacity }),
      });
      const data = await res.json();

      if (data.success && data.summary) {
        showNotification(
          `Analysis Complete! Detected ${data.summary.duplicate_records} duplicates across ${data.summary.total_records} records in ${data.summary.processing_time_ms} ms.`,
          "success"
        );
        window.DashboardManager.updateMetrics(data.summary);
        window.DashboardManager.fetchDuplicateGroups();
        window.DashboardManager.fetchUniqueRecords();
        window.DashboardManager.fetchRawRecords();
        window.VisualizationManager.fetchHashTableState();
      } else {
        showNotification(data.error || "Analysis failed.", "error");
      }
    } catch (err) {
      showNotification("Error running analysis: " + err.message, "error");
    }
  }

  async function loadSampleData() {
    showNotification("Loading multi-format sample datasets (CSV, JSON, TSV, XLSX, TXT, DOCX, PDF)...", "info");

    try {
      const res = await fetch("/api/load-sample", { method: "POST" });
      const data = await res.json();

      if (data.success) {
        showNotification(
          `Loaded ${data.loaded_files.length} heterogeneous datasets! ${data.summary.duplicate_records} duplicates found.`,
          "success"
        );
        window.UploadManager.renderFileCards(data.loaded_files);
        window.DashboardManager.updateMetrics(data.summary);
        window.DashboardManager.fetchDuplicateGroups();
        window.DashboardManager.fetchUniqueRecords();
        window.DashboardManager.fetchRawRecords();
        window.VisualizationManager.fetchHashTableState();
      } else {
        showNotification("Failed to load sample datasets.", "error");
      }
    } catch (err) {
      showNotification("Error loading samples: " + err.message, "error");
    }
  }

  async function resetState() {
    try {
      const res = await fetch("/api/reset", { method: "POST" });
      const data = await res.json();
      if (data.success) {
        showNotification("Session cleared and reset.", "info");
        window.UploadManager.renderFileCards([]);
        window.DashboardManager.updateMetrics({
          total_files_analyzed: 0,
          total_records: 0,
          unique_records: 0,
          duplicate_records: 0,
          duplicate_percentage: 0,
          exact_duplicates: 0,
          partial_duplicates: 0,
          possible_duplicates: 0,
          processing_time_ms: 0,
          hash_table_statistics: { total_collisions: 0 },
          file_reports: [],
        });
        window.DashboardManager.renderDuplicateGroups();
        window.DashboardManager.fetchUniqueRecords();
        window.DashboardManager.fetchRawRecords();
        window.VisualizationManager.fetchHashTableState();
      }
    } catch (err) {
      showNotification("Failed to reset session: " + err.message, "error");
    }
  }

  async function fetchDashboardSummary() {
    try {
      const res = await fetch("/api/results");
      const data = await res.json();
      if (data.success && data.summary) {
        window.DashboardManager.updateMetrics(data.summary);
      }
    } catch (err) {
      // No analysis run yet, clean state is normal
    }
  }

  function setupModal() {
    const backdrop = document.getElementById("record-modal-backdrop");
    const closeBtn = document.getElementById("modal-close-btn");

    if (closeBtn && backdrop) {
      closeBtn.addEventListener("click", () => backdrop.classList.add("hidden"));
      backdrop.addEventListener("click", (e) => {
        if (e.target === backdrop) backdrop.classList.add("hidden");
      });
    }
  }

  async function openRecordModal(recordId) {
    const backdrop = document.getElementById("record-modal-backdrop");
    const title = document.getElementById("modal-record-title");
    const body = document.getElementById("modal-record-body");

    if (!backdrop || !body) return;

    body.innerHTML = '<div class="empty-state">Loading record details...</div>';
    backdrop.classList.remove("hidden");

    try {
      const res = await fetch(`/api/record/${recordId}/trace`);
      const data = await res.json();

      if (!data.success || !data.data) {
        body.innerHTML = `<div class="notification-banner error">${data.error || 'Failed to fetch details'}</div>`;
        return;
      }

      const r = data.data.record;
      const t = data.data.trace;

      title.textContent = `Record #${r.id} (${r.source_file})`;

      let rawRows = "";
      for (const [k, v] of Object.entries(r.raw_data || {})) {
        rawRows += `<tr><td><strong>${escapeHtml(k)}</strong></td><td>${escapeHtml(String(v))}</td></tr>`;
      }

      let canonRows = "";
      for (const [k, v] of Object.entries(r.canonical_data || {})) {
        canonRows += `<tr><td><strong>${escapeHtml(k)}</strong></td><td>${escapeHtml(String(v))}</td></tr>`;
      }

      body.innerHTML = `
        <div style="margin-bottom:12px;">
          ${r.is_duplicate 
            ? `<span class="badge badge-danger">DUPLICATE OF RECORD #${r.duplicate_of_id}</span>` 
            : `<span class="badge badge-success">UNIQUE MASTER RECORD</span>`}
          <span class="badge badge-info" style="margin-left:8px;">${r.file_type}</span>
          <span class="badge badge-primary" style="margin-left:8px;">Bucket [${t ? t.bucket_index : '-'}]</span>
        </div>

        <h4 style="font-size:14px; margin-top:14px; margin-bottom:6px;">Normalized Hash Key:</h4>
        <div style="background:#f1f5f9; padding:8px 12px; border-radius:6px; font-family:var(--font-mono); font-size:12px; word-break:break-all;">
          ${escapeHtml(r.primary_hash_key || '-')}
        </div>

        <h4 style="font-size:14px; margin-top:16px; margin-bottom:6px;">Canonical Standardized Attributes:</h4>
        <table class="data-table" style="margin-bottom:14px;">
          <tbody>${canonRows || '<tr><td>No canonical fields</td></tr>'}</tbody>
        </table>

        <h4 style="font-size:14px; margin-top:16px; margin-bottom:6px;">Raw Input Attributes:</h4>
        <table class="data-table">
          <tbody>${rawRows}</tbody>
        </table>
      `;
    } catch (err) {
      body.innerHTML = `<div class="notification-banner error">Error: ${err.message}</div>`;
    }
  }

  function showNotification(message, type = "info") {
    const banner = document.getElementById("notification-banner");
    if (!banner) return;

    if (notificationTimeout) clearTimeout(notificationTimeout);

    banner.className = `notification-banner ${type}`;
    banner.textContent = message;
    banner.classList.remove("hidden");

    notificationTimeout = setTimeout(() => {
      banner.classList.add("hidden");
    }, 6000);
  }

  function escapeHtml(str) {
    return String(str || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  document.addEventListener("DOMContentLoaded", init);

  return {
    init,
    switchToTab,
    runAnalysis,
    loadSampleData,
    resetState,
    fetchDashboardSummary,
    openRecordModal,
    showNotification,
  };
})();

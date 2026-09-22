/**
 * Dashboard & Records Management Module
 * Controls summary metrics, duplicate groups, unique records table, and raw records explorer.
 */

window.DashboardManager = (function () {
  let uniquePage = 1;
  let uniquePerPage = 15;
  let rawPage = 1;
  let rawPerPage = 15;

  function init() {
    // Unique table search and pagination
    const uniqueSearch = document.getElementById("unique-search-input");
    if (uniqueSearch) {
      uniqueSearch.addEventListener("input", debounce(() => {
        uniquePage = 1;
        fetchUniqueRecords();
      }, 300));
    }

    const btnUniquePrev = document.getElementById("btn-unique-prev");
    const btnUniqueNext = document.getElementById("btn-unique-next");
    if (btnUniquePrev) {
      btnUniquePrev.addEventListener("click", () => {
        if (uniquePage > 1) {
          uniquePage--;
          fetchUniqueRecords();
        }
      });
    }
    if (btnUniqueNext) {
      btnUniqueNext.addEventListener("click", () => {
        uniquePage++;
        fetchUniqueRecords();
      });
    }

    // Raw records search, filter, and pagination
    const rawSearch = document.getElementById("raw-search-input");
    const rawFilter = document.getElementById("select-raw-filter");
    if (rawSearch) {
      rawSearch.addEventListener("input", debounce(() => {
        rawPage = 1;
        fetchRawRecords();
      }, 300));
    }
    if (rawFilter) {
      rawFilter.addEventListener("change", () => {
        rawPage = 1;
        fetchRawRecords();
      });
    }

    const btnRawPrev = document.getElementById("btn-raw-prev");
    const btnRawNext = document.getElementById("btn-raw-next");
    if (btnRawPrev) {
      btnRawPrev.addEventListener("click", () => {
        if (rawPage > 1) {
          rawPage--;
          fetchRawRecords();
        }
      });
    }
    if (btnRawNext) {
      btnRawNext.addEventListener("click", () => {
        rawPage++;
        fetchRawRecords();
      });
    }

    // Duplicate groups search
    const dupSearch = document.getElementById("dup-search-input");
    if (dupSearch) {
      dupSearch.addEventListener("input", debounce(() => {
        renderDuplicateGroups(dupSearch.value.trim());
      }, 300));
    }
  }

  function updateMetrics(summary) {
    if (!summary) return;

    setText("val-total-files", summary.total_files_analyzed || 0);
    setText("val-total-records", summary.total_records || 0);
    setText("val-unique-records", summary.unique_records || 0);
    setText("val-duplicate-records", summary.duplicate_records || 0);
    setText("val-duplicate-pct", (summary.duplicate_percentage || 0) + "%");
    setText("val-collisions", summary.hash_table_statistics ? summary.hash_table_statistics.total_collisions : 0);
    setText("val-processing-time", (summary.processing_time_ms || 0) + " ms");

    setText("count-exact", summary.exact_duplicates || 0);
    setText("count-partial", summary.partial_duplicates || 0);
    setText("count-possible", summary.possible_duplicates || 0);

    setText("badge-dup-count", summary.duplicate_records || 0);
    setText("badge-uniq-count", summary.unique_records || 0);

    renderFileSources(summary.file_reports || []);
  }

  function renderFileSources(reports) {
    const container = document.getElementById("file-sources-container");
    const countEl = document.getElementById("file-sources-count");
    if (!container) return;

    container.innerHTML = "";
    if (!reports || reports.length === 0) {
      container.innerHTML = '<div class="empty-state">No files processed yet.</div>';
      if (countEl) countEl.textContent = "0 files loaded";
      return;
    }

    if (countEl) countEl.textContent = `${reports.length} files processed`;

    reports.forEach((r) => {
      const div = document.createElement("div");
      div.className = "file-item";
      const ext = r.filename.split(".").pop().toUpperCase();
      div.innerHTML = `
        <div class="file-item-left">
          <span class="file-tag">${ext}</span>
          <strong>${escapeHtml(r.filename)}</strong>
        </div>
        <div>
          ${r.status === "success" 
            ? `<span class="badge badge-success">${r.record_count} records</span>` 
            : `<span class="badge badge-danger">${escapeHtml(r.error || 'Error')}</span>`}
        </div>
      `;
      container.appendChild(div);
    });
  }

  let cachedGroups = [];

  async function fetchDuplicateGroups() {
    try {
      const res = await fetch("/api/duplicates");
      const data = await res.json();
      cachedGroups = data.groups || [];
      renderDuplicateGroups();
    } catch (err) {
      console.error("Failed to fetch duplicate groups:", err);
    }
  }

  function renderDuplicateGroups(query = "") {
    const container = document.getElementById("duplicate-groups-container");
    if (!container) return;
    container.innerHTML = "";

    let groups = cachedGroups;
    if (query) {
      const q = query.toLowerCase();
      groups = groups.filter((g) => {
        const primMatch = Object.values(g.primary_record.raw_data || {}).some(v => String(v).toLowerCase().includes(q));
        const dupMatch = g.duplicates.some(d => Object.values(d.raw_data || {}).some(v => String(v).toLowerCase().includes(q)));
        return primMatch || dupMatch || g.matched_fields.some(f => f.toLowerCase().includes(q));
      });
    }

    if (!groups || groups.length === 0) {
      container.innerHTML = '<div class="empty-state">No duplicate groups found. The dataset is either unique or not analyzed yet.</div>';
      return;
    }

    groups.forEach((g) => {
      const card = document.createElement("div");
      card.className = "group-card";

      let typeBadge = '<span class="badge badge-danger">Exact Match (100%)</span>';
      if (g.duplicate_type === "partial") {
        typeBadge = `<span class="badge badge-warning">Partial Match (${Math.round(g.confidence * 100)}%)</span>`;
      } else if (g.duplicate_type === "possible") {
        typeBadge = `<span class="badge badge-info">Possible Match (${Math.round(g.confidence * 100)}%)</span>`;
      }

      const p = g.primary_record;
      const matchedText = g.matched_fields.length > 0 
        ? `Matched on key(s): <strong>${g.matched_fields.join(", ")}</strong>` 
        : "Matched on normalized primary composite key";

      let dupHtml = "";
      g.duplicates.forEach((d) => {
        dupHtml += `
          <div class="rec-entry duplicate">
            <div>
              <strong>Duplicate Record #${d.id}</strong> (from <em>${escapeHtml(d.source_file)}</em> - line ${d.raw_data.__line_number__ || '?'})
              <div style="font-size:12px; color:#475569; margin-top:2px;">
                ${summarizeRecord(d.raw_data)}
              </div>
            </div>
            <button class="btn btn-sm btn-secondary view-trace-btn" data-record-id="${d.id}">Trace Hash</button>
          </div>
        `;
      });

      card.innerHTML = `
        <div class="group-header">
          <div class="group-title">
            <span>Group #${g.group_id}</span>
            ${typeBadge}
          </div>
          <span style="font-size:12px; color:#64748b;">${matchedText}</span>
        </div>
        <div class="group-body">
          <div class="records-sublist">
            <div class="rec-entry master">
              <div>
                <strong>Primary / Master Record #${p.id}</strong> (from <em>${escapeHtml(p.source_file)}</em> - line ${p.raw_data.__line_number__ || '?'})
                <div style="font-size:12px; color:#15803d; margin-top:2px;">
                  ${summarizeRecord(p.raw_data)}
                </div>
              </div>
              <button class="btn btn-sm btn-secondary view-trace-btn" data-record-id="${p.id}">Trace Hash</button>
            </div>
            ${dupHtml}
          </div>
        </div>
      `;

      container.appendChild(card);
    });

    // Attach trace button events
    container.querySelectorAll(".view-trace-btn").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        const rId = parseInt(e.target.getAttribute("data-record-id"), 10);
        window.App.switchToTab("visualization");
        window.VisualizationManager.traceRecord(rId);
      });
    });
  }

  async function fetchUniqueRecords() {
    const searchInput = document.getElementById("unique-search-input");
    const search = searchInput ? searchInput.value.trim() : "";

    try {
      const res = await fetch(`/api/records?type=unique&page=${uniquePage}&per_page=${uniquePerPage}&search=${encodeURIComponent(search)}`);
      const data = await res.json();
      renderUniqueTable(data);
    } catch (err) {
      console.error("Failed to fetch unique records:", err);
    }
  }

  function renderUniqueTable(data) {
    const tbody = document.getElementById("unique-table-body");
    const pageInfo = document.getElementById("unique-page-info");
    const btnPrev = document.getElementById("btn-unique-prev");
    const btnNext = document.getElementById("btn-unique-next");

    if (!tbody) return;
    tbody.innerHTML = "";

    const records = data.records || [];
    if (records.length === 0) {
      tbody.innerHTML = '<tr><td colspan="8" class="empty-state">No unique records found.</td></tr>';
      if (pageInfo) pageInfo.textContent = "Showing 0 of 0";
      if (btnPrev) btnPrev.disabled = true;
      if (btnNext) btnNext.disabled = true;
      return;
    }

    records.forEach((r) => {
      const row = document.createElement("tr");
      const c = r.canonical_data || {};
      const bucketNum = r.hash_trace ? r.hash_trace.bucket_index : "-";

      row.innerHTML = `
        <td><strong>#${r.id}</strong></td>
        <td><span class="file-tag">${r.file_type}</span> ${escapeHtml(r.source_file)}</td>
        <td><strong>${escapeHtml(c.name || '-')}</strong></td>
        <td>${escapeHtml(c.email || '-')}</td>
        <td>${escapeHtml(c.phone || '-')}</td>
        <td>${escapeHtml(c.department || '-')}</td>
        <td><span class="badge badge-info">Bucket ${bucketNum}</span></td>
        <td>
          <button class="btn btn-sm btn-secondary view-record-btn" data-record-id="${r.id}">Inspect</button>
        </td>
      `;
      tbody.appendChild(row);
    });

    // Pagination info
    const start = (data.page - 1) * data.per_page + 1;
    const end = Math.min(data.page * data.per_page, data.total_count);
    if (pageInfo) pageInfo.textContent = `Showing ${start}–${end} of ${data.total_count} master records`;
    if (btnPrev) btnPrev.disabled = data.page <= 1;
    if (btnNext) btnNext.disabled = data.page >= data.total_pages;

    // Attach inspect handlers
    tbody.querySelectorAll(".view-record-btn").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        const id = parseInt(e.target.getAttribute("data-record-id"), 10);
        window.App.openRecordModal(id);
      });
    });
  }

  async function fetchRawRecords() {
    const filterSelect = document.getElementById("select-raw-filter");
    const searchInput = document.getElementById("raw-search-input");
    const rType = filterSelect ? filterSelect.value : "all";
    const search = searchInput ? searchInput.value.trim() : "";

    try {
      const res = await fetch(`/api/records?type=${rType}&page=${rawPage}&per_page=${rawPerPage}&search=${encodeURIComponent(search)}`);
      const data = await res.json();
      renderRawTable(data);
    } catch (err) {
      console.error("Failed to fetch raw records:", err);
    }
  }

  function renderRawTable(data) {
    const tbody = document.getElementById("raw-table-body");
    const pageInfo = document.getElementById("raw-page-info");
    const btnPrev = document.getElementById("btn-raw-prev");
    const btnNext = document.getElementById("btn-raw-next");

    if (!tbody) return;
    tbody.innerHTML = "";

    const records = data.records || [];
    if (records.length === 0) {
      tbody.innerHTML = '<tr><td colspan="6" class="empty-state">No records found.</td></tr>';
      if (pageInfo) pageInfo.textContent = "Showing 0 of 0";
      if (btnPrev) btnPrev.disabled = true;
      if (btnNext) btnNext.disabled = true;
      return;
    }

    records.forEach((r) => {
      const row = document.createElement("tr");
      const isDup = r.is_duplicate;
      const statusBadge = isDup 
        ? `<span class="badge badge-danger">Duplicate of #${r.duplicate_of_id}</span>` 
        : `<span class="badge badge-success">Unique Master</span>`;

      row.innerHTML = `
        <td><strong>#${r.id}</strong></td>
        <td><span class="file-tag">${r.file_type}</span> ${escapeHtml(r.source_file)}</td>
        <td>${statusBadge}</td>
        <td><code style="font-size:11px;">${summarizeRecord(r.raw_data)}</code></td>
        <td><code style="font-size:11px; color:#2563eb;">${escapeHtml(r.primary_hash_key || '-')}</code></td>
        <td>
          <button class="btn btn-sm btn-secondary view-trace-btn" data-record-id="${r.id}">Trace</button>
        </td>
      `;
      tbody.appendChild(row);
    });

    const start = (data.page - 1) * data.per_page + 1;
    const end = Math.min(data.page * data.per_page, data.total_count);
    if (pageInfo) pageInfo.textContent = `Showing ${start}–${end} of ${data.total_count} records`;
    if (btnPrev) btnPrev.disabled = data.page <= 1;
    if (btnNext) btnNext.disabled = data.page >= data.total_pages;

    tbody.querySelectorAll(".view-trace-btn").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        const id = parseInt(e.target.getAttribute("data-record-id"), 10);
        window.App.switchToTab("visualization");
        window.VisualizationManager.traceRecord(id);
      });
    });
  }

  function summarizeRecord(raw) {
    if (!raw) return "-";
    const parts = [];
    for (const [k, v] of Object.entries(raw)) {
      if (k.startsWith("__")) continue;
      parts.push(`${k}: ${v}`);
    }
    return escapeHtml(parts.slice(0, 4).join(" | "));
  }

  function setText(id, text) {
    const el = document.getElementById(id);
    if (el) el.textContent = text;
  }

  function debounce(func, wait) {
    let timeout;
    return function (...args) {
      clearTimeout(timeout);
      timeout = setTimeout(() => func.apply(this, args), wait);
    };
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
    updateMetrics,
    fetchDuplicateGroups,
    fetchUniqueRecords,
    fetchRawRecords,
  };
})();

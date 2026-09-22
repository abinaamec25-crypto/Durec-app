/**
 * Hashing Visualization & Mathematical Trace Module
 * Anna University Regulation 2025 Data Structures Project.
 */

window.VisualizationManager = (function () {
  let traceSelectEl = null;

  function init() {
    traceSelectEl = document.getElementById("select-trace-record");
    if (traceSelectEl) {
      traceSelectEl.addEventListener("change", (e) => {
        const rId = parseInt(e.target.value, 10);
        if (rId) {
          traceRecord(rId);
        }
      });
    }
  }

  async function fetchHashTableState() {
    try {
      const res = await fetch("/api/hash-table?max_buckets=50");
      const data = await res.json();
      if (data.success && data.hash_table) {
        renderHashTable(data.hash_table);
      }
    } catch (err) {
      console.error("Failed to load hash table state:", err);
    }
  }

  function renderHashTable(htData) {
    const stats = htData.statistics || {};
    const buckets = htData.buckets || [];

    // Update stats bar
    setText("vis-stat-m", stats.capacity || 0);
    setText("vis-stat-n", stats.num_elements || 0);
    setText("vis-stat-alpha", stats.load_factor !== undefined ? stats.load_factor.toFixed(3) : "0.000");
    setText("vis-stat-collisions", stats.total_collisions || 0);
    setText("vis-stat-maxchain", stats.max_chain_length || 0);
    setText("vis-stat-empty", stats.empty_buckets || 0);

    const infoBadge = document.getElementById("vis-table-info");
    if (infoBadge) {
      infoBadge.textContent = `${stats.algorithm ? stats.algorithm.toUpperCase() : 'HASH'} | α = ${stats.load_factor}`;
    }

    // Render bucket grid
    const grid = document.getElementById("bucket-grid");
    if (!grid) return;
    grid.innerHTML = "";

    if (buckets.length === 0) {
      grid.innerHTML = '<div class="empty-state">No hash table data available. Run analysis first.</div>';
      return;
    }

    buckets.forEach((b) => {
      const card = document.createElement("div");
      let statusClass = "empty";
      if (b.chain_length > 1) {
        statusClass = "collision";
      } else if (b.chain_length === 1) {
        statusClass = "occupied";
      }
      card.className = `bucket-card ${statusClass}`;

      let chainHtml = "";
      if (b.chain_length === 0) {
        chainHtml = '<span class="text-muted" style="font-size:11px;">[Empty Slot - NULL]</span>';
      } else {
        chainHtml = '<div class="chain-flow">';
        b.nodes.forEach((node, idx) => {
          if (idx > 0) {
            chainHtml += '<div class="node-arrow">&darr; next (collision)</div>';
          }
          chainHtml += `
            <div class="chain-node">
              <span><strong>#${node.record_id}</strong> (${escapeHtml(node.source)})</span>
              <button class="btn btn-sm btn-secondary" onclick="window.VisualizationManager.traceRecord(${node.record_id})" style="padding:1px 6px; font-size:10px;">Trace</button>
            </div>
          `;
        });
        chainHtml += '</div>';
      }

      card.innerHTML = `
        <div class="bucket-head">
          <span>Bucket [${b.bucket_index}]</span>
          <span class="badge ${b.chain_length > 1 ? 'badge-warning' : (b.chain_length === 1 ? 'badge-success' : 'badge-info')}">
            ${b.chain_length} node${b.chain_length === 1 ? '' : 's'}
          </span>
        </div>
        ${chainHtml}
      `;
      grid.appendChild(card);
    });

    populateTraceSelector();
  }

  async function populateTraceSelector() {
    if (!traceSelectEl) return;
    try {
      const res = await fetch("/api/records?type=all&per_page=100");
      const data = await res.json();
      const records = data.records || [];

      traceSelectEl.innerHTML = '<option value="">-- Choose a record to visualize --</option>';
      records.forEach((r) => {
        const opt = document.createElement("option");
        opt.value = r.id;
        const name = (r.canonical_data && r.canonical_data.name) || `Record #${r.id}`;
        opt.textContent = `#${r.id} - ${name} (${r.source_file}) [${r.is_duplicate ? 'Duplicate' : 'Master'}]`;
        traceSelectEl.appendChild(opt);
      });
    } catch (err) {
      console.error("Failed to populate trace selector:", err);
    }
  }

  async function traceRecord(recordId) {
    const traceDisplay = document.getElementById("trace-display");
    if (!traceDisplay) return;

    if (traceSelectEl) {
      traceSelectEl.value = recordId;
    }

    traceDisplay.innerHTML = '<div class="empty-state">Computing mathematical hash trace...</div>';

    try {
      const res = await fetch(`/api/record/${recordId}/trace`);
      const data = await res.json();

      if (!data.success || !data.data) {
        traceDisplay.innerHTML = `<div class="notification-banner error">${data.error || 'Failed to retrieve trace'}</div>`;
        return;
      }

      renderTraceDetails(data.data.record, data.data.trace);
    } catch (err) {
      traceDisplay.innerHTML = `<div class="notification-banner error">Error: ${err.message}</div>`;
    }
  }

  function renderTraceDetails(record, trace) {
    const traceDisplay = document.getElementById("trace-display");
    if (!traceDisplay) return;

    if (!trace) {
      traceDisplay.innerHTML = '<div class="empty-state">Trace data not available for this record.</div>';
      return;
    }

    const steps = trace.calculation_steps || [];
    const previewSteps = steps.slice(0, 12); // Show first 12 character steps for clarity

    let stepsRows = "";
    previewSteps.forEach((s) => {
      stepsRows += `
        <tr>
          <td>${s.step}</td>
          <td>'${escapeHtml(s.char)}' (${s.ascii})</td>
          <td>${escapeHtml(s.formula)}</td>
          <td><strong>${s.hash_accum}</strong></td>
        </tr>
      `;
    });

    if (steps.length > 12) {
      stepsRows += `
        <tr>
          <td colspan="4" style="text-align:center; color:#64748b;">
            ... [${steps.length - 12} additional character multiplication steps omitted for brevity] ...
          </td>
        </tr>
      `;
    }

    const statusBadge = record.is_duplicate 
      ? `<span class="badge badge-danger">DUPLICATE OF RECORD #${record.duplicate_of_id}</span>` 
      : `<span class="badge badge-success">UNIQUE MASTER RECORD</span>`;

    traceDisplay.innerHTML = `
      <div style="margin-bottom:16px; display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:8px;">
        <h4 style="color:#0f172a;">Tracing Record #${record.id} (${escapeHtml(record.source_file)})</h4>
        ${statusBadge}
      </div>

      <div class="trace-flow-grid">
        <div class="trace-box">
          <div class="trace-box-title">1. Raw Input String</div>
          <div class="trace-box-content">${escapeHtml(record.primary_hash_key)}</div>
        </div>

        <div class="trace-box">
          <div class="trace-box-title">2. Hash Function Formula</div>
          <div class="trace-box-content">${escapeHtml(trace.algorithm_name)}</div>
        </div>

        <div class="trace-box">
          <div class="trace-box-title">3. Raw Integer Hash H(s)</div>
          <div class="trace-box-content"><strong>${trace.raw_hash}</strong> (0x${Number(trace.raw_hash).toString(16).toUpperCase()})</div>
        </div>

        <div class="trace-box" style="border-color:#bbf7d0; background-color:#fcfdfc;">
          <div class="trace-box-title">4. Modulo Bucket Index</div>
          <div class="trace-box-content">
            <code>${trace.raw_hash} % ${trace.table_capacity}</code> = 
            <strong style="font-size:16px; color:#15803d;">Bucket [${trace.bucket_index}]</strong>
          </div>
        </div>
      </div>

      <div class="trace-box" style="margin-top:12px;">
        <div class="trace-box-title">5. Chain Traversal & Collision Resolution</div>
        <div class="trace-box-content" style="font-size:13px; font-family:var(--font-family);">
          <p>
            ${trace.collision_occurred 
              ? `⚠ <strong>Collision Occurred!</strong> Bucket [${trace.bucket_index}] was already occupied. Traversed separate chain with <strong>${trace.comparisons_made} string comparison(s)</strong>.` 
              : `✓ <strong>No Collision.</strong> Bucket [${trace.bucket_index}] was empty or first in chain.`}
          </p>
          <p style="margin-top:6px; color:#475569;">
            ${record.is_duplicate 
              ? `Matched duplicate with identical normalized key already registered at this bucket. Appended to Duplicate Group.` 
              : `Key verified unique along bucket chain. Inserted new Node as master record.`}
          </p>
        </div>
      </div>

      <div style="margin-top:16px;">
        <h5 style="font-size:13px; font-weight:700; margin-bottom:6px;">Polynomial Character-by-Character Accumulator:</h5>
        <div class="table-responsive">
          <table class="trace-steps-table">
            <thead>
              <tr>
                <th>Step (i)</th>
                <th>Character (ASCII)</th>
                <th>Mathematical Operation</th>
                <th>Accumulator mod 2^32</th>
              </tr>
            </thead>
            <tbody>
              ${stepsRows}
            </tbody>
          </table>
        </div>
      </div>
    `;
  }

  function setText(id, text) {
    const el = document.getElementById(id);
    if (el) el.textContent = text;
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
    fetchHashTableState,
    traceRecord,
  };
})();

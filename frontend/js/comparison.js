/* ============================================================
   Stay or Leave — Comparison page behavior
   ============================================================ */

(function () {
  'use strict';

  let placeASelection = null; // { id, name, slug, type }
  let placeBSelection = null;
  let searchDebounce = {};

  function escapeHtml(str) {
    return window.SOL.ui.escapeHtml(str);
  }

  /* ---------- Place autocomplete ---------- */
  function initPlacePicker(inputId, resultsId, hiddenId, onSelect) {
    const input = document.getElementById(inputId);
    const results = document.getElementById(resultsId);
    const hidden = document.getElementById(hiddenId);

    input.addEventListener('input', () => {
      hidden.value = '';
      const query = input.value.trim();
      clearTimeout(searchDebounce[inputId]);
      if (query.length < 2) {
        results.classList.remove('is-open');
        return;
      }
      searchDebounce[inputId] = setTimeout(() => searchPlaces(query, results, input, hidden, onSelect), 250);
    });

    input.addEventListener('blur', () => {
      setTimeout(() => results.classList.remove('is-open'), 150);
    });

    input.addEventListener('focus', () => {
      if (results.innerHTML) results.classList.add('is-open');
    });
  }

  async function searchPlaces(query, resultsEl, inputEl, hiddenEl, onSelect) {
    try {
      const data = await window.SOL.api.get(`/places?search=${encodeURIComponent(query)}&per_page=8`);
      if (!data.places || !data.places.length) {
        resultsEl.innerHTML = `<div class="place-picker__result" style="color:var(--text-dim);">No matches found</div>`;
        resultsEl.classList.add('is-open');
        return;
      }
      resultsEl.innerHTML = data.places
        .map(
          (p) => `
          <button type="button" class="place-picker__result" data-id="${p.id}" data-name="${escapeHtml(p.name)}" data-slug="${p.slug}">
            ${escapeHtml(p.name)} <span>${p.type}</span>
          </button>`
        )
        .join('');
      resultsEl.classList.add('is-open');

      resultsEl.querySelectorAll('.place-picker__result[data-id]').forEach((btn) => {
        btn.addEventListener('click', () => {
          inputEl.value = btn.dataset.name;
          hiddenEl.value = btn.dataset.id;
          resultsEl.classList.remove('is-open');
          onSelect({ id: btn.dataset.id, name: btn.dataset.name, slug: btn.dataset.slug });
        });
      });
    } catch (err) {
      resultsEl.innerHTML = `<div class="place-picker__result" style="color:var(--danger);">Couldn't load results</div>`;
      resultsEl.classList.add('is-open');
    }
  }

  /* ---------- Compare submission ---------- */
  function initCompareForm() {
    const form = document.getElementById('compare-form');
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      runComparison();
    });
  }

  async function runComparison() {
    const aInput = document.getElementById('place-a-input').value.trim();
    const bInput = document.getElementById('place-b-input').value.trim();
    const aId = document.getElementById('place-a-id').value;
    const bId = document.getElementById('place-b-id').value;

    const placeAParam = aId || aInput;
    const placeBParam = bId || bInput;

    if (!placeAParam || !placeBParam) {
      window.SOL.ui.showToast('Choose two places to compare', 'error');
      return;
    }

    const resultsMount = document.getElementById('compare-results');
    resultsMount.innerHTML = `<p style="color:var(--text-dim);">Comparing...</p>`;

    try {
      const data = await window.SOL.api.get(
        `/comparisons/compare?place_a=${encodeURIComponent(placeAParam)}&place_b=${encodeURIComponent(placeBParam)}`
      );
      renderComparison(data);
    } catch (err) {
      resultsMount.innerHTML = `
        <div class="card compare-empty">
          <svg viewBox="0 0 24 24" fill="none" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><path d="M12 8v4M12 16h.01"/></svg>
          <p>${escapeHtml(err.message || "Couldn't run that comparison. Try a different place name.")}</p>
        </div>`;
    }
  }

  function renderComparison(data) {
    const { place_a, place_b, rows, recommendation, summary } = data;
    const recName = recommendation === 'A' ? place_a.name : recommendation === 'B' ? place_b.name : null;

    const maxValues = {};
    rows.forEach((r) => {
      maxValues[r.key] = Math.max(r.value_a || 0, r.value_b || 0, 1);
    });

    const barsHtml = rows
      .map((r) => {
        const pctA = ((r.value_a || 0) / maxValues[r.key]) * 100;
        const pctB = ((r.value_b || 0) / maxValues[r.key]) * 100;
        return `
          <div class="bar-row">
            <div class="bar-row__label">${escapeHtml(r.label)}</div>
            <div class="bar-row__track bar-row__track--a">
              <span class="bar-row__value">${formatValue(r.value_a, r.unit)}</span>
              <div class="bar-row__bar" style="width:${pctA}%;"></div>
            </div>
            <div class="bar-row__track bar-row__track--b">
              <div class="bar-row__bar" style="width:${pctB}%;"></div>
              <span class="bar-row__value">${formatValue(r.value_b, r.unit)}</span>
            </div>
          </div>`;
      })
      .join('');

    const tableRowsHtml = rows
      .map(
        (r) => `
        <tr>
          <td>${escapeHtml(r.label)}</td>
          <td class="${r.winner === 'A' ? 'is-winner' : ''}">${formatValue(r.value_a, r.unit)}</td>
          <td class="${r.winner === 'B' ? 'is-winner' : ''}">${formatValue(r.value_b, r.unit)}</td>
        </tr>`
      )
      .join('');

    const exportUrl = `${window.STAY_OR_LEAVE_API_BASE || '/api'}/comparisons/export-pdf?place_a=${encodeURIComponent(
      place_a.slug
    )}&place_b=${encodeURIComponent(place_b.slug)}`;

    document.getElementById('compare-results').innerHTML = `
      <div class="result-header reveal is-visible">
        <h2>${escapeHtml(place_a.name)} vs ${escapeHtml(place_b.name)}</h2>
        <div class="result-header__actions">
          <button class="btn btn--ghost btn--sm" id="bookmark-btn">Bookmark</button>
          <a class="btn btn--ghost btn--sm" href="${exportUrl}" target="_blank" rel="noopener">Export as PDF</a>
        </div>
      </div>

      <div class="recommendation-banner reveal is-visible">
        <div class="recommendation-banner__badge">${recName ? escapeHtml(recName) : 'Too close to call'}</div>
        <p class="recommendation-banner__text">${escapeHtml(summary)}</p>
      </div>

      <div class="card chart-card reveal is-visible">
        <h3>Factor by factor</h3>
        <div class="chart-legend">
          <span><i class="legend-dot legend-dot--a"></i>${escapeHtml(place_a.name)}</span>
          <span><i class="legend-dot legend-dot--b"></i>${escapeHtml(place_b.name)}</span>
        </div>
        ${barsHtml}
      </div>

      <div class="card compare-table-wrap reveal is-visible">
        <table class="compare-table">
          <thead>
            <tr><th>Factor</th><th>${escapeHtml(place_a.name)}</th><th>${escapeHtml(place_b.name)}</th></tr>
          </thead>
          <tbody>${tableRowsHtml}</tbody>
        </table>
      </div>
    `;

    document.getElementById('bookmark-btn').addEventListener('click', () => saveAndBookmark(place_a, place_b));
  }

  function formatValue(value, unit) {
    if (value === null || value === undefined) return '—';
    if (unit === 'USD') return `$${Number(value).toLocaleString()}`;
    if (unit === 'percent') return `${value}%`;
    if (unit === 'mbps') return `${value} Mbps`;
    if (unit === 'index_0_10') return `${value}/10`;
    if (unit === 'index_0_100') return `${value}/100`;
    return String(value);
  }

  async function saveAndBookmark(placeA, placeB) {
    if (!window.SOL.auth.getAccessToken()) {
      window.SOL.ui.showToast('Log in to bookmark comparisons', 'info');
      return;
    }
    try {
      const created = await window.SOL.api.post('/comparisons', { place_a: placeA.id, place_b: placeB.id });
      await window.SOL.api.post(`/comparisons/${created.comparison.id}/bookmark`, {});
      window.SOL.ui.showToast('Comparison bookmarked', 'success');
    } catch (err) {
      window.SOL.ui.showToast(err.message || 'Could not bookmark this comparison', 'error');
    }
  }

  /* ---------- Prefill from query params (?a=Canada&b=Germany) ---------- */
  function prefillFromQuery() {
    const params = new URLSearchParams(window.location.search);
    const a = params.get('a');
    const b = params.get('b');
    if (a) document.getElementById('place-a-input').value = a;
    if (b) document.getElementById('place-b-input').value = b;
    if (a && b) runComparison();
  }

  document.addEventListener('DOMContentLoaded', () => {
    initPlacePicker('place-a-input', 'place-a-results', 'place-a-id', (sel) => (placeASelection = sel));
    initPlacePicker('place-b-input', 'place-b-results', 'place-b-id', (sel) => (placeBSelection = sel));
    initCompareForm();
    prefillFromQuery();
  });
})();

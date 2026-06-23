/* ============================================================
   Stay or Leave — Place detail page behavior
   ============================================================ */

(function () {
  'use strict';

  let currentPlace = null;
  let currentPage = 1;
  let currentSort = 'newest';
  let currentSearch = '';
  let selectedRating = 0;

  function escapeHtml(str) {
    return window.SOL.ui.escapeHtml(str);
  }

  function getSlugFromQuery() {
    const params = new URLSearchParams(window.location.search);
    return params.get('slug') || params.get('place');
  }

  async function loadPlace() {
    const slug = getSlugFromQuery();
    if (!slug) {
      document.getElementById('place-name').textContent = 'Place not found';
      return;
    }
    try {
      const data = await window.SOL.api.get(`/places/${encodeURIComponent(slug)}`);
      currentPlace = data.place;
      renderHeader();
      renderMetrics();
      document.getElementById('compare-link').href = `comparison.html?a=${encodeURIComponent(currentPlace.slug)}`;
      loadReviews();
    } catch (err) {
      document.getElementById('place-name').textContent = 'Place not found';
      document.getElementById('metrics-grid').innerHTML = `<p style="color:var(--danger);">${escapeHtml(err.message || 'Could not load this place')}</p>`;
    }
  }

  function renderHeader() {
    document.querySelector('#place-header .eyebrow').textContent = currentPlace.type;
    document.getElementById('place-name').textContent = currentPlace.name;
    document.title = `${currentPlace.name} — Stay or Leave`;
  }

  const METRIC_LABELS = {
    cost_of_living: ['Cost of Living', 'index_0_100'],
    avg_salary: ['Average Salary', 'USD'],
    tax_rate: ['Tax Rate', 'percent'],
    safety_index: ['Safety', 'index_0_100'],
    healthcare_index: ['Healthcare', 'index_0_100'],
    internet_speed: ['Internet Speed', 'mbps'],
    happiness_index: ['Happiness Index', 'index_0_10'],
    pollution_index: ['Pollution', 'index_0_100'],
    gdp_per_capita: ['GDP per Capita', 'USD'],
  };

  function formatValue(value, unit) {
    if (value === null || value === undefined) return '—';
    if (unit === 'USD') return `$${Number(value).toLocaleString()}`;
    if (unit === 'percent') return `${value}%`;
    if (unit === 'mbps') return `${value} Mbps`;
    if (unit === 'index_0_10') return `${value}/10`;
    if (unit === 'index_0_100') return `${value}/100`;
    return String(value);
  }

  function renderMetrics() {
    const mount = document.getElementById('metrics-grid');
    const metrics = currentPlace.metrics || {};
    const keys = Object.keys(METRIC_LABELS).filter((k) => metrics[k] !== undefined && metrics[k] !== null);

    if (!keys.length) {
      mount.innerHTML = `<p style="color:var(--text-dim);">No metrics recorded for this place yet.</p>`;
      return;
    }

    mount.innerHTML = keys
      .map((key) => {
        const [label, unit] = METRIC_LABELS[key];
        return `
          <div class="metric-tile reveal is-visible">
            <div class="metric-tile__label">${escapeHtml(label)}</div>
            <div class="metric-tile__value mono">${formatValue(metrics[key], unit)}</div>
          </div>`;
      })
      .join('');
  }

  /* ---------- Review form ---------- */
  function initReviewFormToggle() {
    const writeBtn = document.getElementById('write-review-btn');
    const cancelBtn = document.getElementById('review-cancel-btn');
    const section = document.getElementById('review-form-section');

    writeBtn.addEventListener('click', () => {
      if (!window.SOL.auth.getAccessToken()) {
        window.SOL.ui.showToast('Log in to write a review', 'info');
        window.location.href = `login.html?next=place.html?slug=${encodeURIComponent(currentPlace.slug)}`;
        return;
      }
      section.hidden = !section.hidden;
      if (!section.hidden) section.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });

    cancelBtn.addEventListener('click', () => {
      section.hidden = true;
      document.getElementById('review-form').reset();
      selectedRating = 0;
      updateStarDisplay();
    });
  }

  function initStarRating() {
    const buttons = document.querySelectorAll('#review-star-rating button');
    buttons.forEach((btn) => {
      btn.addEventListener('click', () => {
        selectedRating = Number(btn.dataset.value);
        document.getElementById('review-rating').value = String(selectedRating);
        updateStarDisplay();
      });
    });
  }

  function updateStarDisplay() {
    document.querySelectorAll('#review-star-rating button').forEach((btn) => {
      btn.classList.toggle('is-active', Number(btn.dataset.value) <= selectedRating);
    });
  }

  function setFieldError(fieldId, hasError) {
    const field = document.getElementById(fieldId);
    if (field) field.classList.toggle('has-error', hasError);
  }

  function initReviewSubmit() {
    const form = document.getElementById('review-form');
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const title = document.getElementById('review-title').value.trim();
      const body = document.getElementById('review-body').value.trim();
      const rating = selectedRating;

      const titleOk = title.length >= 3;
      const bodyOk = body.length >= 10;
      const ratingOk = rating >= 1 && rating <= 5;
      setFieldError('review-title-field', !titleOk);
      setFieldError('review-body-field', !bodyOk);
      setFieldError('review-rating-field', !ratingOk);
      if (!titleOk || !bodyOk || !ratingOk) return;

      const btn = document.getElementById('review-submit-btn');
      btn.disabled = true;
      btn.textContent = 'Posting...';
      try {
        await window.SOL.api.post('/reviews', {
          place_id: currentPlace.id,
          title,
          body,
          rating,
        });
        window.SOL.ui.showToast('Review posted — thanks for sharing', 'success');
        form.reset();
        selectedRating = 0;
        updateStarDisplay();
        document.getElementById('review-form-section').hidden = true;
        currentPage = 1;
        loadReviews();
      } catch (err) {
        window.SOL.ui.showToast(err.message || 'Could not post your review', 'error');
      } finally {
        btn.disabled = false;
        btn.textContent = 'Post review';
      }
    });
  }

  /* ---------- Reviews list ---------- */
  async function loadReviews(append = false) {
    const mount = document.getElementById('reviews-list');
    if (!append) mount.innerHTML = `<p style="color:var(--text-dim);">Loading reviews…</p>`;

    try {
      const params = new URLSearchParams({
        place_id: currentPlace.id,
        sort: currentSort,
        page: String(currentPage),
        per_page: '10',
      });
      if (currentSearch) params.set('search', currentSearch);

      const data = await window.SOL.api.get(`/reviews?${params.toString()}`);
      const html = (data.reviews || []).map(renderReviewCard).join('');

      if (!append) {
        mount.innerHTML = html || `<p style="color:var(--text-dim);">No reviews yet — be the first to share your experience.</p>`;
      } else {
        mount.insertAdjacentHTML('beforeend', html);
      }

      const loadMoreBtn = document.getElementById('load-more-btn');
      loadMoreBtn.hidden = currentPage >= (data.total_pages || 1);

      attachReviewCardHandlers();
    } catch (err) {
      mount.innerHTML = `<p style="color:var(--danger);">${escapeHtml(err.message || 'Could not load reviews')}</p>`;
    }
  }

  function renderReviewCard(review) {
    const stars = '★'.repeat(review.rating) + '☆'.repeat(5 - review.rating);
    const imagesHtml = (review.images || [])
      .map((url) => `<img src="${url}" alt="">`)
      .join('');

    return `
      <div class="card review-card reveal is-visible" data-review-id="${review.id}">
        <div class="review-card__top">
          <div>
            <div class="review-card__stars">${stars}</div>
            <h3 class="review-card__title">${escapeHtml(review.title)}</h3>
          </div>
        </div>
        <p class="review-card__body">${escapeHtml(review.body)}</p>
        ${imagesHtml ? `<div class="review-card__images">${imagesHtml}</div>` : ''}
        <div class="review-card__meta">
          <span class="review-card__author">
            <span class="review-card__avatar"></span>
            ${escapeHtml(review.author_name)}
          </span>
          <span>${new Date(review.created_at).toLocaleDateString()}</span>
          <div class="review-card__actions">
            <button class="like-btn ${review.liked_by_viewer ? 'is-liked' : ''}" data-action="like">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 9V5a3 3 0 00-3-3l-4 9v11h11.28a2 2 0 002-1.7l1.38-9a2 2 0 00-2-2.3zM7 22H4a2 2 0 01-2-2v-7a2 2 0 012-2h3"/></svg>
              <span data-helpful-count>${review.helpful_count}</span> Helpful
            </button>
            <button data-action="toggle-comments">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 11.5a8.38 8.38 0 01-.9 3.8 8.5 8.5 0 01-7.6 4.7 8.38 8.38 0 01-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 01-.9-3.8 8.5 8.5 0 014.7-7.6 8.38 8.38 0 013.8-.9h.5a8.48 8.48 0 018 8v.5z"/></svg>
              ${review.comment_count} Comments
            </button>
            <button data-action="report">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/><path d="M4 22V15"/></svg>
              Report
            </button>
          </div>
        </div>
        <div class="review-card__comments" hidden>
          <div data-comments-list><p style="color:var(--text-dim); font-size:0.85rem;">Loading comments…</p></div>
          <form class="comment-form" data-comment-form>
            <input type="text" placeholder="Add a comment" maxlength="1000" required>
            <button type="submit" class="btn btn--ghost btn--sm">Post</button>
          </form>
        </div>
      </div>`;
  }

  function attachReviewCardHandlers() {
    document.querySelectorAll('.review-card').forEach((card) => {
      const reviewId = card.dataset.reviewId;
      if (card.dataset.boundHandlers) return;
      card.dataset.boundHandlers = 'true';

      card.querySelector('[data-action="like"]').addEventListener('click', () => toggleLike(reviewId, card));
      card.querySelector('[data-action="toggle-comments"]').addEventListener('click', () => toggleComments(reviewId, card));
      card.querySelector('[data-action="report"]').addEventListener('click', () => reportReview(reviewId));
      card.querySelector('[data-comment-form]').addEventListener('submit', (e) => submitComment(e, reviewId, card));
    });
  }

  async function toggleLike(reviewId, card) {
    if (!window.SOL.auth.getAccessToken()) {
      window.SOL.ui.showToast('Log in to mark a review helpful', 'info');
      return;
    }
    try {
      const data = await window.SOL.api.post(`/reviews/${reviewId}/like`, {});
      const btn = card.querySelector('[data-action="like"]');
      btn.classList.toggle('is-liked', data.liked);
      btn.querySelector('[data-helpful-count]').textContent = data.helpful_count;
    } catch (err) {
      window.SOL.ui.showToast(err.message || 'Could not update like', 'error');
    }
  }

  async function toggleComments(reviewId, card) {
    const panel = card.querySelector('.review-card__comments');
    panel.hidden = !panel.hidden;
    if (!panel.hidden && !panel.dataset.loaded) {
      panel.dataset.loaded = 'true';
      try {
        const data = await window.SOL.api.get(`/reviews/${reviewId}/comments`);
        const listEl = panel.querySelector('[data-comments-list]');
        listEl.innerHTML = (data.comments || [])
          .map(
            (c) => `
            <div class="comment-item">
              <span class="comment-item__avatar"></span>
              <div><span class="comment-item__author">${escapeHtml(c.author_name)}</span>${escapeHtml(c.body)}</div>
            </div>`
          )
          .join('') || `<p style="color:var(--text-dim); font-size:0.85rem;">No comments yet.</p>`;
      } catch (err) {
        panel.querySelector('[data-comments-list]').innerHTML = `<p style="color:var(--danger); font-size:0.85rem;">Could not load comments</p>`;
      }
    }
  }

  async function submitComment(e, reviewId, card) {
    e.preventDefault();
    if (!window.SOL.auth.getAccessToken()) {
      window.SOL.ui.showToast('Log in to comment', 'info');
      return;
    }
    const input = e.target.querySelector('input');
    const body = input.value.trim();
    if (!body) return;

    try {
      const data = await window.SOL.api.post(`/reviews/${reviewId}/comments`, { body });
      const listEl = card.querySelector('[data-comments-list]');
      const empty = listEl.querySelector('p');
      if (empty) empty.remove();
      listEl.insertAdjacentHTML(
        'beforeend',
        `<div class="comment-item">
          <span class="comment-item__avatar"></span>
          <div><span class="comment-item__author">${escapeHtml(data.comment.author_name)}</span>${escapeHtml(data.comment.body)}</div>
        </div>`
      );
      input.value = '';
    } catch (err) {
      window.SOL.ui.showToast(err.message || 'Could not post comment', 'error');
    }
  }

  async function reportReview(reviewId) {
    if (!window.SOL.auth.getAccessToken()) {
      window.SOL.ui.showToast('Log in to report a review', 'info');
      return;
    }
    const reason = window.prompt('Briefly tell us what\'s wrong with this review:');
    if (!reason || !reason.trim()) return;
    try {
      await window.SOL.api.post(`/reviews/${reviewId}/report`, { reason: reason.trim() });
      window.SOL.ui.showToast('Thanks — our team will take a look', 'success');
    } catch (err) {
      window.SOL.ui.showToast(err.message || 'Could not submit report', 'error');
    }
  }

  function initSearchAndSort() {
    const searchInput = document.getElementById('review-search');
    const sortSelect = document.getElementById('review-sort');
    let debounce;

    searchInput.addEventListener('input', () => {
      clearTimeout(debounce);
      debounce = setTimeout(() => {
        currentSearch = searchInput.value.trim();
        currentPage = 1;
        loadReviews();
      }, 300);
    });

    sortSelect.addEventListener('change', () => {
      currentSort = sortSelect.value;
      currentPage = 1;
      loadReviews();
    });

    document.getElementById('load-more-btn').addEventListener('click', () => {
      currentPage += 1;
      loadReviews(true);
    });
  }

  document.addEventListener('DOMContentLoaded', () => {
    loadPlace();
    initReviewFormToggle();
    initStarRating();
    initReviewSubmit();
    initSearchAndSort();
  });
})();

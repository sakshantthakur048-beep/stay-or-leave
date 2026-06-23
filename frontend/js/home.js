/* ============================================================
   Stay or Leave — Home page behavior
   ============================================================ */

(function () {
  'use strict';

  function initHeroSearch() {
    const form = document.getElementById('hero-search-form');
    if (!form) return;
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const query = document.getElementById('hero-search-input').value.trim();
      if (!query) {
        window.location.href = 'comparison.html';
        return;
      }
      // "Canada vs Germany" -> prefill both sides on the comparison page
      const parts = query.split(/\s+vs\.?\s+/i);
      const params = new URLSearchParams();
      if (parts[0]) params.set('a', parts[0].trim());
      if (parts[1]) params.set('b', parts[1].trim());
      window.location.href = `comparison.html?${params.toString()}`;
    });
  }

  function initFaqAccordion() {
    document.querySelectorAll('.faq-item__q').forEach((btn) => {
      btn.addEventListener('click', () => {
        const item = btn.closest('.faq-item');
        const isOpen = item.getAttribute('data-open') === 'true';
        item.setAttribute('data-open', String(!isOpen));
        btn.setAttribute('aria-expanded', String(!isOpen));
      });
    });
  }

  async function loadFeaturedComparisons() {
    const mount = document.getElementById('featured-comparisons');
    if (!mount) return;
    try {
      const data = await window.SOL.api.get('/comparisons/featured');
      if (!data.comparisons || !data.comparisons.length) return; // keep static fallback cards

      mount.innerHTML = data.comparisons
        .map((c) => {
          const a = c.place_a ? c.place_a.name : 'Place A';
          const b = c.place_b ? c.place_b.name : 'Place B';
          const recName = c.recommendation === 'A' ? a : c.recommendation === 'B' ? b : 'Either';
          return `
            <a href="comparison.html?a=${encodeURIComponent(a)}&b=${encodeURIComponent(b)}" class="card compare-card reveal is-visible">
              <div class="compare-card__sides">
                <span class="compare-card__side">${window.SOL.ui.escapeHtml(a)}</span>
                <span class="compare-card__vs">vs</span>
                <span class="compare-card__side">${window.SOL.ui.escapeHtml(b)}</span>
              </div>
              <p class="compare-card__rec">Recommendation: <strong>${window.SOL.ui.escapeHtml(recName)}</strong></p>
            </a>`;
        })
        .join('');
    } catch (err) {
      // Network/API not reachable yet — static fallback cards already in the HTML stay visible.
      console.warn('Could not load featured comparisons:', err.message);
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    initHeroSearch();
    initFaqAccordion();
    loadFeaturedComparisons();
  });
})();

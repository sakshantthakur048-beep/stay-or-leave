/* ============================================================
   Stay or Leave — Shared UI behaviors
   Runs on every page: theme toggle, mobile nav, toasts,
   scroll-reveal animations, and reflecting auth state in the navbar.
   ============================================================ */

(function () {
  'use strict';

  /* ---------- Theme ---------- */
  function initTheme() {
    const saved = localStorage.getItem('sol_theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const theme = saved || (prefersDark ? 'dark' : 'light');
    document.documentElement.setAttribute('data-theme', theme);

    const toggle = document.querySelector('.theme-toggle');
    if (!toggle) return;
    updateToggleIcon(toggle, theme);

    toggle.addEventListener('click', () => {
      const current = document.documentElement.getAttribute('data-theme');
      const next = current === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
      localStorage.setItem('sol_theme', next);
      updateToggleIcon(toggle, next);
    });
  }

  function updateToggleIcon(toggle, theme) {
    toggle.innerHTML = theme === 'dark'
      ? '<svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/></svg>'
      : '<svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round"><path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/></svg>';
    toggle.setAttribute('aria-label', theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
  }

  /* ---------- Mobile nav ---------- */
  function initMobileNav() {
    const burger = document.querySelector('.navbar__burger');
    const navbar = document.querySelector('.navbar');
    if (!burger || !navbar) return;
    burger.addEventListener('click', () => {
      const isOpen = navbar.classList.toggle('is-open');
      burger.setAttribute('aria-expanded', String(isOpen));
    });
  }

  /* ---------- Toasts ---------- */
  function ensureToastRegion() {
    let region = document.getElementById('toast-region');
    if (!region) {
      region = document.createElement('div');
      region.id = 'toast-region';
      region.setAttribute('role', 'status');
      region.setAttribute('aria-live', 'polite');
      document.body.appendChild(region);
    }
    return region;
  }

  function showToast(message, type = 'info', duration = 4000) {
    const region = ensureToastRegion();
    const toast = document.createElement('div');
    toast.className = `toast toast--${type}`;
    toast.textContent = message;
    region.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transition = 'opacity 200ms ease';
      setTimeout(() => toast.remove(), 220);
    }, duration);
  }

  /* ---------- Scroll reveal ---------- */
  function initScrollReveal() {
    const items = document.querySelectorAll('.reveal');
    if (!items.length) return;

    if (!('IntersectionObserver' in window)) {
      items.forEach((el) => el.classList.add('is-visible'));
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-visible');
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.15, rootMargin: '0px 0px -40px 0px' }
    );

    items.forEach((el) => observer.observe(el));
  }

  /* ---------- Navbar auth state ---------- */
  function initNavAuthState() {
    const slot = document.querySelector('[data-nav-auth-slot]');
    if (!slot) return;

    const user = window.SOL.auth.getCachedUser();
    if (user) {
      slot.innerHTML = `
        <a href="profile.html" class="btn btn--ghost btn--sm" style="display:flex;align-items:center;gap:6px;">
          ${user.profile_picture
            ? `<img src="${user.profile_picture}" alt="" style="width:22px;height:22px;border-radius:50%;object-fit:cover;">`
            : ''}
          ${escapeHtml(user.name.split(' ')[0])}
        </a>
        <button class="btn btn--ghost btn--sm" data-logout>Log out</button>
      `;
      const logoutBtn = slot.querySelector('[data-logout]');
      logoutBtn.addEventListener('click', async () => {
        try { await window.SOL.api.post('/auth/logout', {}); } catch {}
        window.SOL.auth.clearTokens();
        window.location.href = 'index.html';
      });
    } else {
      slot.innerHTML = `
        <a href="login.html" class="btn btn--ghost btn--sm">Log in</a>
        <a href="signup.html" class="btn btn--primary btn--sm">Sign up</a>
      `;
    }
  }

  function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  /* ---------- Init ---------- */
  document.addEventListener('DOMContentLoaded', () => {
    initScrollReveal();
    // initTheme/initMobileNav/initNavAuthState need navbar markup, which
    // layout.js injects after DOMContentLoaded — see sol:layout-ready below.
    // Still call them here too, in case a page has no #site-navbar mount
    // and includes static nav markup directly.
    initTheme();
    initMobileNav();
    initNavAuthState();
  });

  document.addEventListener('sol:layout-ready', () => {
    initTheme();
    initMobileNav();
    initNavAuthState();
  });

  window.SOL = window.SOL || {};
  window.SOL.ui = { showToast, escapeHtml };
})();

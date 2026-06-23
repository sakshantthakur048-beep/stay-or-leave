/* ============================================================
   Stay or Leave — Layout partials
   Injects the navbar and footer markup into placeholder elements
   so nav/footer changes happen in one file, not six.
   ============================================================ */

(function () {
  'use strict';

  const LOGO_SVG = `
    <svg viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M14 2v24" stroke="var(--text)" stroke-width="1.5" stroke-linecap="round"/>
      <path d="M14 6L4 9.5L7 18C7 18 10 20.5 14 20.5" stroke="var(--stay)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
      <path d="M14 6L24 9.5L21 18C21 18 18 20.5 14 20.5" stroke="var(--leave)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
    </svg>`;

  function navHTML(active) {
    const links = [
      ['index.html', 'Home'],
      ['comparison.html', 'Compare'],
      ['about.html', 'About'],
      ['contact.html', 'Contact'],
    ];
    const linkHtml = links
      .map(
        ([href, label]) =>
          `<a href="${href}" ${active === href ? 'aria-current="page"' : ''}>${label}</a>`
      )
      .join('');

    return `
      <div class="container" style="display:flex;align-items:center;justify-content:space-between;width:100%;">
        <a href="index.html" class="navbar__logo">
          <span class="logo-mark">${LOGO_SVG}</span>
          Stay or Leave
        </a>
        <nav class="navbar__links" aria-label="Primary">${linkHtml}</nav>
        <div class="navbar__actions">
          <div data-nav-auth-slot style="display:flex;gap:8px;"></div>
          <button class="theme-toggle" aria-label="Toggle dark mode"></button>
          <button class="navbar__burger" aria-label="Open menu" aria-expanded="false">
            <span></span><span></span><span></span>
          </button>
        </div>
      </div>`;
  }

  function footerHTML() {
    return `
      <div class="container">
        <div class="footer__grid">
          <div>
            <div class="footer__brand">Stay or Leave</div>
            <p class="footer__tagline">A clearer way to decide between two places, two offers, two paths — backed by the numbers, not just gut feeling.</p>
          </div>
          <div>
            <h4>Explore</h4>
            <ul>
              <li><a href="comparison.html">Compare places</a></li>
              <li><a href="index.html#popular">Popular countries</a></li>
              <li><a href="index.html#stats">Statistics</a></li>
            </ul>
          </div>
          <div>
            <h4>Company</h4>
            <ul>
              <li><a href="about.html">About us</a></li>
              <li><a href="contact.html">Contact</a></li>
              <li><a href="about.html#faq">FAQ</a></li>
            </ul>
          </div>
          <div>
            <h4>Legal</h4>
            <ul>
              <li><a href="privacy.html">Privacy policy</a></li>
              <li><a href="terms.html">Terms &amp; conditions</a></li>
            </ul>
          </div>
        </div>
        <div class="footer__bottom">
          <span>&copy; ${new Date().getFullYear()} Stay or Leave. All rights reserved.</span>
          <div class="footer__socials">
            <a href="#" aria-label="Twitter"><svg viewBox="0 0 24 24" fill="none" stroke-width="2"><path d="M23 3a10.9 10.9 0 01-3.14 1.53A4.48 4.48 0 0012 8v1A10.66 10.66 0 013 4s-4 9 5 13a11.64 11.64 0 01-7 2c9 5 20 0 20-11.5a4.5 4.5 0 00-.08-.83A6.13 6.13 0 0023 3z"/></svg></a>
            <a href="#" aria-label="Instagram"><svg viewBox="0 0 24 24" fill="none" stroke-width="2"><rect x="2" y="2" width="20" height="20" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1"/></svg></a>
            <a href="#" aria-label="LinkedIn"><svg viewBox="0 0 24 24" fill="none" stroke-width="2"><path d="M16 8a6 6 0 016 6v7h-4v-7a2 2 0 00-2-2 2 2 0 00-2 2v7h-4V8h4v1.5A5 5 0 0116 8z"/><rect x="2" y="9" width="4" height="12"/><circle cx="4" cy="4" r="2"/></svg></a>
          </div>
        </div>
      </div>`;
  }

  document.addEventListener('DOMContentLoaded', () => {
    const navMount = document.getElementById('site-navbar');
    if (navMount) {
      navMount.innerHTML = navHTML(navMount.getAttribute('data-active'));
    }
    const footerMount = document.getElementById('site-footer');
    if (footerMount) {
      footerMount.innerHTML = footerHTML();
    }

    // Re-run UI init steps that depend on the just-injected nav markup.
    document.dispatchEvent(new CustomEvent('sol:layout-ready'));
  });
})();

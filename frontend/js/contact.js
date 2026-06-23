/* ============================================================
   Stay or Leave — Contact page behavior
   ============================================================ */

(function () {
  'use strict';

  function setFieldError(fieldId, hasError) {
    const field = document.getElementById(fieldId);
    if (field) field.classList.toggle('has-error', hasError);
  }

  function isValidEmail(value) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value.trim());
  }

  function initContactForm() {
    const form = document.getElementById('contact-form');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const name = document.getElementById('name').value.trim();
      const email = document.getElementById('email').value;
      const subject = document.getElementById('subject').value.trim();
      const message = document.getElementById('message').value.trim();

      const nameOk = name.length > 0;
      const emailOk = isValidEmail(email);
      const messageOk = message.length >= 5;
      setFieldError('name-field', !nameOk);
      setFieldError('email-field', !emailOk);
      setFieldError('message-field', !messageOk);
      if (!nameOk || !emailOk || !messageOk) return;

      const btn = document.getElementById('contact-submit-btn');
      btn.disabled = true;
      btn.textContent = 'Sending...';
      try {
        await window.SOL.api.post('/contact', { name, email, subject, message });
        window.SOL.ui.showToast("Thanks for reaching out — we'll get back to you soon", 'success');
        form.reset();
      } catch (err) {
        window.SOL.ui.showToast(err.message || 'Could not send your message', 'error');
      } finally {
        btn.disabled = false;
        btn.textContent = 'Send message';
      }
    });
  }

  /* ---------- Live chat widget (lightweight, canned-response demo) ---------- */
  function initLiveChat() {
    const toggle = document.getElementById('live-chat-toggle');
    const panel = document.getElementById('live-chat-panel');
    const closeBtn = document.getElementById('live-chat-close');
    const form = document.getElementById('live-chat-form');
    const input = document.getElementById('live-chat-input');
    const body = document.getElementById('live-chat-body');
    if (!toggle || !panel) return;

    toggle.addEventListener('click', () => {
      panel.hidden = !panel.hidden;
      if (!panel.hidden) input.focus();
    });
    closeBtn.addEventListener('click', () => (panel.hidden = true));

    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const text = input.value.trim();
      if (!text) return;

      appendMessage(text, 'user');
      input.value = '';

      setTimeout(() => {
        appendMessage(
          "Thanks for the message — this is a demo widget, so for a real answer please use the contact form above or email hello@stayorleave.com.",
          'bot'
        );
      }, 500);
    });

    function appendMessage(text, role) {
      const div = document.createElement('div');
      div.className = `live-chat-msg live-chat-msg--${role}`;
      div.textContent = text;
      body.appendChild(div);
      body.scrollTop = body.scrollHeight;
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    initContactForm();
    initLiveChat();
  });
})();
